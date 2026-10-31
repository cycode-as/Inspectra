"""
Preprocessing Module - Background-Agnostic Feature Extraction

Fixes Issue #1: Background Sensitivity & Domain Shift
Provides utilities to neutralize background and focus on object regions.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class BackgroundRemover:
    """
    Background removal utilities for object-focused anomaly detection.
    
    Implements multiple strategies to neutralize background influence:
    1. GrabCut-based background removal
    2. Adaptive thresholding-based segmentation
    3. Edge-based object detection
    """
    
    def __init__(self, method: str = "grabcut"):
        """
        Initialize background remover.
        
        Args:
            method: Background removal method ("grabcut", "threshold", "edge", "none")
        """
        self.method = method
        logger.info(f"BackgroundRemover initialized with method: {method}")
    
    def remove_background(
        self,
        image: np.ndarray,
        return_mask: bool = False
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Remove background from image.
        
        Args:
            image: Input image (H, W, 3) in RGB format
            return_mask: Whether to return the foreground mask
            
        Returns:
            Tuple of (processed_image, mask) where mask is None if return_mask=False
        """
        if self.method == "none":
            return image, None if not return_mask else np.ones(image.shape[:2], dtype=np.uint8)
        
        elif self.method == "grabcut":
            return self._grabcut_removal(image, return_mask)
        
        elif self.method == "threshold":
            return self._threshold_removal(image, return_mask)
        
        elif self.method == "edge":
            return self._edge_removal(image, return_mask)
        
        else:
            logger.warning(f"Unknown method {self.method}, using original image")
            return image, None if not return_mask else np.ones(image.shape[:2], dtype=np.uint8)
    
    def _grabcut_removal(
        self,
        image: np.ndarray,
        return_mask: bool
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        GrabCut-based background removal.
        
        Assumes object is in the center region of the image.
        """
        h, w = image.shape[:2]
        
        # Define initial rectangle (center 70% of image)
        margin_h, margin_w = int(h * 0.15), int(w * 0.15)
        rect = (margin_w, margin_h, w - 2*margin_w, h - 2*margin_h)
        
        # Initialize mask
        mask = np.zeros(image.shape[:2], np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        try:
            # Apply GrabCut
            cv2.grabCut(
                image,
                mask,
                rect,
                bgd_model,
                fgd_model,
                5,  # iterations
                cv2.GC_INIT_WITH_RECT
            )
            
            # Create binary mask (0 and 2 = background, 1 and 3 = foreground)
            mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
            
            # Apply mask to image (replace background with neutral gray)
            result = image.copy()
            result[mask2 == 0] = [128, 128, 128]  # Neutral gray background
            
            logger.debug("GrabCut background removal successful")
            return result, mask2 if return_mask else None
            
        except Exception as e:
            logger.warning(f"GrabCut failed: {e}, using original image")
            return image, None if not return_mask else np.ones(image.shape[:2], dtype=np.uint8)
    
    def _threshold_removal(
        self,
        image: np.ndarray,
        return_mask: bool
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Adaptive thresholding-based background removal.
        
        Works well for objects with distinct contrast from background.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply Otsu's thresholding
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Convert to binary (0 or 1)
        mask = (mask > 127).astype(np.uint8)
        
        # Apply mask to image
        result = image.copy()
        result[mask == 0] = [128, 128, 128]  # Neutral gray background
        
        logger.debug("Threshold background removal successful")
        return result, mask if return_mask else None
    
    def _edge_removal(
        self,
        image: np.ndarray,
        return_mask: bool
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Edge-based object detection and background removal.
        
        Uses Canny edge detection + contour finding.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create mask from largest contour
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            cv2.drawContours(mask, [largest_contour], -1, 1, thickness=cv2.FILLED)
        else:
            # If no contours found, use center region
            h, w = image.shape[:2]
            margin_h, margin_w = int(h * 0.15), int(w * 0.15)
            mask[margin_h:h-margin_h, margin_w:w-margin_w] = 1
        
        # Apply mask to image
        result = image.copy()
        result[mask == 0] = [128, 128, 128]  # Neutral gray background
        
        logger.debug("Edge-based background removal successful")
        return result, mask if return_mask else None


def apply_focus_mask(
    anomaly_map: np.ndarray,
    object_mask: np.ndarray,
    blur_sigma: float = 3.0
) -> np.ndarray:
    """
    Apply object focus mask to anomaly map to reduce background influence.
    
    Args:
        anomaly_map: Anomaly heatmap (H, W)
        object_mask: Binary object mask (H, W) with 1 = object, 0 = background
        blur_sigma: Gaussian blur sigma for smooth transition
        
    Returns:
        Masked anomaly map with reduced background influence
    """
    # Resize mask to match anomaly map if needed
    if object_mask.shape != anomaly_map.shape:
        object_mask = cv2.resize(
            object_mask.astype(np.float32),
            (anomaly_map.shape[1], anomaly_map.shape[0]),
            interpolation=cv2.INTER_LINEAR
        )
    
    # Apply Gaussian blur for smooth transition
    if blur_sigma > 0:
        object_mask = cv2.GaussianBlur(
            object_mask.astype(np.float32),
            (0, 0),
            blur_sigma
        )
    
    # Apply mask (reduce background anomalies)
    masked_anomaly_map = anomaly_map * object_mask
    
    return masked_anomaly_map


def normalize_image_to_tensor(
    image: np.ndarray,
    mean: Tuple[float, float, float] = (0.485, 0.456, 0.406),
    std: Tuple[float, float, float] = (0.229, 0.224, 0.225)
) -> np.ndarray:
    """
    Normalize image with ImageNet statistics (Fixes Issue #4).
    
    Args:
        image: Input image (H, W, 3) in RGB format with values [0, 255]
        mean: Channel-wise mean (ImageNet default)
        std: Channel-wise standard deviation (ImageNet default)
        
    Returns:
        Normalized image array (H, W, 3) with proper scaling
    """
    # Convert to float and scale to [0, 1]
    image_float = image.astype(np.float32) / 255.0
    
    # Apply channel-wise normalization
    mean_array = np.array(mean, dtype=np.float32).reshape(1, 1, 3)
    std_array = np.array(std, dtype=np.float32).reshape(1, 1, 3)
    
    normalized = (image_float - mean_array) / std_array
    
    logger.debug(f"Image normalized: shape={normalized.shape}, "
                f"min={normalized.min():.3f}, max={normalized.max():.3f}, "
                f"mean={normalized.mean():.3f}")
    
    return normalized
