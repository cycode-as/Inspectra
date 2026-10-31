"""
Normalization Module - Adaptive Anomaly Score Calibration

Fixes Issue #2: Anomaly Score Saturation
Implements dynamic calibration with percentile-based bounds.
"""

import numpy as np
from pathlib import Path
import json
import logging
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class AdaptiveScoreNormalizer:
    """
    Adaptive anomaly score normalizer with dynamic calibration.
    
    Maintains running statistics of anomaly distances and uses
    percentile-based normalization to avoid saturation.
    """
    
    def __init__(
        self,
        stats_file: Optional[Path] = None,
        percentile_max: float = 95.0,
        percentile_min: float = 5.0,
        buffer_size: int = 1000
    ):
        """
        Initialize adaptive normalizer.
        
        Args:
            stats_file: Path to save/load statistics
            percentile_max: Percentile for max bound (e.g., 95 = 95th percentile)
            percentile_min: Percentile for min bound (e.g., 5 = 5th percentile)
            buffer_size: Maximum number of scores to keep in buffer
        """
        self.stats_file = stats_file or Path("ai_module/results/score_stats.json")
        self.percentile_max = percentile_max
        self.percentile_min = percentile_min
        self.buffer_size = buffer_size
        
        # Running statistics
        self.score_buffer = []
        self.min_score = 0.0
        self.max_score = 1.0
        self.stats_loaded = False
        
        # Load existing statistics if available
        self._load_stats()
        
        logger.info(f"AdaptiveScoreNormalizer initialized: "
                   f"percentile_min={percentile_min}, percentile_max={percentile_max}, "
                   f"current_bounds=({self.min_score:.4f}, {self.max_score:.4f})")
    
    def _load_stats(self):
        """Load statistics from file if exists."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    self.min_score = data.get('min_score', 0.0)
                    self.max_score = data.get('max_score', 1.0)
                    self.score_buffer = data.get('recent_scores', [])[-self.buffer_size:]
                    self.stats_loaded = True
                    logger.info(f"Loaded statistics from {self.stats_file}: "
                               f"min={self.min_score:.4f}, max={self.max_score:.4f}, "
                               f"buffer_size={len(self.score_buffer)}")
            except Exception as e:
                logger.warning(f"Failed to load statistics: {e}, using defaults")
        else:
            logger.info("No statistics file found, using default bounds")
    
    def _save_stats(self):
        """Save statistics to file."""
        try:
            self.stats_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                'min_score': float(self.min_score),
                'max_score': float(self.max_score),
                'recent_scores': [float(s) for s in self.score_buffer[-self.buffer_size:]],
                'percentile_min': self.percentile_min,
                'percentile_max': self.percentile_max
            }
            with open(self.stats_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved statistics to {self.stats_file}")
        except Exception as e:
            logger.warning(f"Failed to save statistics: {e}")
    
    def update_statistics(self, raw_score: float):
        """
        Update running statistics with new raw score.
        
        Args:
            raw_score: Raw anomaly score from model
        """
        self.score_buffer.append(raw_score)
        
        # Keep buffer size limited
        if len(self.score_buffer) > self.buffer_size:
            self.score_buffer = self.score_buffer[-self.buffer_size:]
        
        # Recalculate bounds if we have enough samples
        if len(self.score_buffer) >= 20:  # Minimum samples for reliable percentiles
            self.min_score = np.percentile(self.score_buffer, self.percentile_min)
            self.max_score = np.percentile(self.score_buffer, self.percentile_max)
            
            # Ensure min < max
            if self.min_score >= self.max_score:
                self.max_score = self.min_score + 0.1
            
            logger.debug(f"Updated bounds: min={self.min_score:.4f}, max={self.max_score:.4f}, "
                        f"buffer_size={len(self.score_buffer)}")
            
            # Save periodically (every 10 updates)
            if len(self.score_buffer) % 10 == 0:
                self._save_stats()
    
    def normalize(
        self,
        raw_score: float,
        update_stats: bool = True,
        clip: bool = True
    ) -> float:
        """
        Normalize raw anomaly score to [0, 1] range with adaptive bounds.
        
        Args:
            raw_score: Raw anomaly score from model
            update_stats: Whether to update statistics with this score
            clip: Whether to clip result to [0, 1]
            
        Returns:
            Normalized score in [0, 1] range
        """
        # Update statistics if enabled
        if update_stats:
            self.update_statistics(raw_score)
        
        # Normalize using current bounds
        if self.max_score - self.min_score > 1e-6:
            normalized = (raw_score - self.min_score) / (self.max_score - self.min_score)
        else:
            # Fallback if bounds are too close
            normalized = 0.5
        
        # Clip to [0, 1] if requested
        if clip:
            normalized = np.clip(normalized, 0.0, 1.0)
        
        logger.debug(f"Normalized score: raw={raw_score:.4f} -> normalized={normalized:.4f}")
        
        return float(normalized)
    
    def get_bounds(self) -> Tuple[float, float]:
        """
        Get current normalization bounds.
        
        Returns:
            Tuple of (min_score, max_score)
        """
        return (self.min_score, self.max_score)
    
    def reset_statistics(self):
        """Reset all statistics to default values."""
        self.score_buffer = []
        self.min_score = 0.0
        self.max_score = 1.0
        self.stats_loaded = False
        logger.info("Statistics reset to defaults")


def smooth_score_mapping(
    score: float,
    pass_threshold: float = 0.35,
    review_threshold: float = 0.65
) -> str:
    """
    Map normalized score to status with smooth thresholds.
    
    Args:
        score: Normalized anomaly score [0, 1]
        pass_threshold: Threshold below which product passes (default: 0.35)
        review_threshold: Threshold above which product is rejected (default: 0.65)
        
    Returns:
        Status: "PASS", "REVIEW", or "REJECT"
    """
    if score < pass_threshold:
        return "PASS"
    elif score < review_threshold:
        return "REVIEW"
    else:
        return "REJECT"


def confidence_aware_status(
    score: float,
    confidence_low: float = 0.3,
    confidence_high: float = 0.7
) -> Tuple[str, str]:
    """
    Determine status with confidence level.
    
    Args:
        score: Normalized anomaly score [0, 1]
        confidence_low: Threshold for low confidence region
        confidence_high: Threshold for high confidence region
        
    Returns:
        Tuple of (status, confidence) where confidence is "high", "medium", or "low"
    """
    if score < confidence_low:
        return "PASS", "high"
    elif score < 0.5:
        return "PASS", "medium"
    elif score < confidence_high:
        return "REVIEW", "medium"
    else:
        return "REJECT", "high"
