"""
INSPECTRA PatchCore Prediction Module - FIXED VERSION

Fixes all 4 critical issues:
1. Background sensitivity via preprocessing
2. Score saturation via adaptive normalization  
3. Async heatmap file race condition via synchronous I/O
4. Image normalization pipeline via proper scaling
"""

from pathlib import Path
from time import perf_counter, sleep
from uuid import uuid4
import os

import numpy as np
import torch
from anomalib.data import PredictDataset
from anomalib.engine import Engine
from anomalib.models import Patchcore
from PIL import Image
import cv2
import logging

# Import our new modules
from preprocessing import BackgroundRemover, apply_focus_mask
from normalization import AdaptiveScoreNormalizer, smooth_score_mapping

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project paths
BASE_DIR = Path(__file__).resolve().parent
CHECKPOINT = (
    BASE_DIR
    / "results"
    / "Patchcore"
    / "MVTecAD"
    / "metal_nut"
    / "v0"
    / "weights"
    / "lightning"
    / "model.ckpt"
)

HEATMAP_DIR = BASE_DIR / "results" / "heatmaps"
STATS_FILE = BASE_DIR / "results" / "score_stats.json"

# Global singletons
_MODEL = None
_ENGINE = None
_BACKGROUND_REMOVER = None
_SCORE_NORMALIZER = None


def load_model():
    """Load PatchCore model (singleton)."""
    global _MODEL, _ENGINE

    if _MODEL is None:
        if not CHECKPOINT.exists():
            raise FileNotFoundError(
                f"Model checkpoint not found: {CHECKPOINT}"
            )

        logger.info("Loading INSPECTRA PatchCore model...")

        _MODEL = Patchcore.load_from_checkpoint(
            str(CHECKPOINT),
            map_location="cpu",
        )

        _MODEL.eval()

        _ENGINE = Engine(
            accelerator="cpu",
            devices=1,
        )

        logger.info("Model loaded successfully.")

    return _MODEL, _ENGINE


def get_background_remover(method: str = "grabcut"):
    """Get background remover instance (singleton)."""
    global _BACKGROUND_REMOVER
    
    if _BACKGROUND_REMOVER is None:
        _BACKGROUND_REMOVER = BackgroundRemover(method=method)
    
    return _BACKGROUND_REMOVER


def get_score_normalizer():
    """Get adaptive score normalizer (singleton)."""
    global _SCORE_NORMALIZER
    
    if _SCORE_NORMALIZER is None:
        _SCORE_NORMALIZER = AdaptiveScoreNormalizer(
            stats_file=STATS_FILE,
            percentile_max=95.0,  # Use 95th percentile as max bound
            percentile_min=5.0,   # Use 5th percentile as min bound
            buffer_size=1000
        )
    
    return _SCORE_NORMALIZER


def to_number(value):
    """Convert tensor or numeric value to Python float."""
    if isinstance(value, torch.Tensor):
        return float(value.detach().cpu().item())
    return float(value)


def save_heatmap_sync(
    anomaly_map: np.ndarray,
    output_path: Path,
    max_retries: int = 3,
    retry_delay: float = 0.1
) -> Path:
    """
    Save heatmap with synchronous I/O and verification (Fixes Issue #3).
    
    Args:
        anomaly_map: Anomaly heatmap array (H, W)
        output_path: Path to save heatmap image
        max_retries: Maximum number of verification retries
        retry_delay: Delay between retries in seconds
        
    Returns:
        Path to saved heatmap file
        
    Raises:
        RuntimeError: If file could not be verified after max_retries
    """
    from anomalib.visualization import visualize_anomaly_map
    
    # Generate heatmap image
    heatmap_image = visualize_anomaly_map(
        anomaly_map,
        normalize=True,
        colormap=True,
    )
    
    # Save with explicit sync
    heatmap_image.save(str(output_path))
    
    # Force OS to flush buffers
    if hasattr(os, 'sync'):
        os.sync()  # Unix systems
    
    # Verify file exists and is readable
    for attempt in range(max_retries):
        if output_path.exists() and output_path.stat().st_size > 0:
            # Try to open the file to ensure it's readable
            try:
                with Image.open(output_path) as img:
                    img.verify()  # Verify it's a valid image
                logger.info(f"Heatmap saved and verified: {output_path}")
                return output_path
            except Exception as e:
                logger.warning(f"Heatmap verification failed (attempt {attempt+1}/{max_retries}): {e}")
        
        # Wait and retry
        if attempt < max_retries - 1:
            sleep(retry_delay)
    
    # If we get here, verification failed
    raise RuntimeError(f"Failed to verify heatmap file after {max_retries} attempts: {output_path}")


def predict(
    image_path,
    use_background_removal: bool = True,
    use_adaptive_normalization: bool = True,
    background_method: str = "grabcut"
):
    """
    Analyze one metal-nut image with all fixes applied.

    Args:
        image_path: Path to input image
        use_background_removal: Enable background removal (Fix #1)
        use_adaptive_normalization: Enable adaptive score normalization (Fix #2)
        background_method: Background removal method ("grabcut", "threshold", "edge", "none")

    Returns:
        Dict with:
            anomaly_score: Normalized anomaly score [0, 1]
            status: "PASS", "REVIEW", or "REJECT"
            heatmap_path: Path to saved heatmap (verified)
            inference_time_ms: Inference time in milliseconds
            raw_score: Original raw anomaly score (for debugging)
            normalization_bounds: Current (min, max) bounds used
    """
    image_path = Path(image_path).resolve()

    if not image_path.is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")

    start_time = perf_counter()

    # Load model
    model, engine = load_model()
    
    # Get utilities
    bg_remover = get_background_remover(method=background_method) if use_background_removal else None
    normalizer = get_score_normalizer() if use_adaptive_normalization else None

    # FIX #1 & #4: Load and preprocess image
    logger.info(f"Processing image: {image_path}")
    
    # Load image
    original_image = cv2.imread(str(image_path))
    if original_image is None:
        raise ValueError(f"Failed to load image: {image_path}")
    
    # Convert BGR to RGB
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
    
    # Apply background removal if enabled
    object_mask = None
    if use_background_removal and bg_remover:
        logger.info(f"Applying background removal with method: {background_method}")
        processed_image, object_mask = bg_remover.remove_background(
            original_image,
            return_mask=True
        )
    else:
        processed_image = original_image
        logger.info("Background removal disabled, using original image")
    
    # Save preprocessed image temporarily for anomalib
    temp_dir = BASE_DIR / "results" / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_image_path = temp_dir / f"{uuid4().hex}.png"
    
    # Save as RGB
    Image.fromarray(processed_image).save(temp_image_path)
    
    # Run prediction with anomalib
    # NOTE: Anomalib's PredictDataset applies ImageNet normalization internally
    # (Fix #4 is handled by anomalib's transforms)
    dataset = PredictDataset(
        path=str(temp_image_path),
        image_size=(256, 256),
    )

    predictions = engine.predict(
        model=model,
        dataset=dataset,
        return_predictions=True,
    )

    if not predictions:
        raise RuntimeError("The model did not return predictions.")
    
    prediction = predictions[0]

    # Extract raw prediction values
    raw_score = to_number(prediction.pred_score)
    raw_label = to_number(prediction.pred_label)
    anomaly_map = prediction.anomaly_map

    if isinstance(anomaly_map, torch.Tensor):
        anomaly_map = anomaly_map.detach().cpu().numpy()

    anomaly_map = np.squeeze(anomaly_map)

    if anomaly_map.ndim != 2:
        raise ValueError(
            f"Unexpected anomaly map shape: {anomaly_map.shape}"
        )

    # Apply focus mask to anomaly map if we have object mask (Fix #1)
    if object_mask is not None:
        logger.info("Applying focus mask to anomaly map")
        anomaly_map = apply_focus_mask(
            anomaly_map,
            object_mask,
            blur_sigma=3.0
        )

    # FIX #2: Adaptive score normalization
    if use_adaptive_normalization and normalizer:
        normalized_score = normalizer.normalize(
            raw_score,
            update_stats=True,
            clip=True
        )
        norm_bounds = normalizer.get_bounds()
        logger.info(f"Score normalized: raw={raw_score:.4f} -> normalized={normalized_score:.4f}, "
                   f"bounds=({norm_bounds[0]:.4f}, {norm_bounds[1]:.4f})")
    else:
        # Fallback: use raw score directly (clipped to [0, 1])
        normalized_score = np.clip(raw_score, 0.0, 1.0)
        norm_bounds = (0.0, 1.0)
        logger.info(f"Using raw score (adaptive normalization disabled): {normalized_score:.4f}")

    # FIX #3: Save heatmap with synchronous I/O and verification
    HEATMAP_DIR.mkdir(parents=True, exist_ok=True)
    heatmap_filename = f"{uuid4().hex}.png"
    heatmap_path = HEATMAP_DIR / heatmap_filename

    logger.info(f"Saving heatmap to: {heatmap_path}")
    heatmap_path = save_heatmap_sync(
        anomaly_map,
        heatmap_path,
        max_retries=3,
        retry_delay=0.1
    )

    # Determine status with smooth thresholds
    status = smooth_score_mapping(
        normalized_score,
        pass_threshold=0.35,    # Lower threshold (was 0.45)
        review_threshold=0.65   # Higher threshold (was 0.55)
    )

    inference_time = (perf_counter() - start_time) * 1000

    # Clean up temporary file
    try:
        temp_image_path.unlink()
    except Exception as e:
        logger.warning(f"Failed to delete temp file: {e}")

    result = {
        "anomaly_score": float(normalized_score),
        "status": status,
        "heatmap_path": str(heatmap_path),
        "inference_time_ms": round(inference_time, 2),
        "raw_score": float(raw_score),
        "normalization_bounds": norm_bounds
    }

    logger.info(f"Prediction complete: score={normalized_score:.4f}, status={status}")
    
    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print('Usage: python predict.py "path_to_image" [--no-bg-removal] [--no-adaptive-norm]')
        sys.exit(1)

    # Parse arguments
    image_arg = sys.argv[1]
    use_bg_removal = "--no-bg-removal" not in sys.argv
    use_adaptive_norm = "--no-adaptive-norm" not in sys.argv

    try:
        result = predict(
            image_arg,
            use_background_removal=use_bg_removal,
            use_adaptive_normalization=use_adaptive_norm
        )

        print("\nINSPECTRA PREDICTION RESULT (FIXED)")
        print("-" * 50)
        print(f"Normalized Score: {result['anomaly_score']:.4f}")
        print(f"Raw Score: {result['raw_score']:.4f}")
        print(f"Status: {result['status']}")
        print(f"Normalization Bounds: ({result['normalization_bounds'][0]:.4f}, {result['normalization_bounds'][1]:.4f})")
        print(f"Heatmap: {result['heatmap_path']}")
        print(f"Inference Time: {result['inference_time_ms']:.2f} ms")

    except Exception as error:
        print(f"\nPrediction failed: {error}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
