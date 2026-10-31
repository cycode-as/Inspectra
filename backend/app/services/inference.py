"""
Inference Service Module

Handles integration with the AI prediction function for defect detection.
Manages prediction execution, result validation, and error handling.
"""

import os
import logging
from typing import Callable, Dict, Any
from pydantic import ValidationError


# Configure logging
logger = logging.getLogger(__name__)


class InferenceError(Exception):
    """Exception raised when inference operations fail."""
    pass


class InferenceService:
    """
    Service for interfacing with external AI prediction function.
    
    Responsibilities:
    - Call external AI prediction function with image path
    - Validate prediction results structure and values
    - Handle and wrap exceptions from AI function
    - Return validated prediction results
    """
    
    def __init__(self, predict_function: Callable[[str], Dict[str, Any]]):
        """
        Initialize the inference service with a prediction function.
        
        Args:
            predict_function: Callable that takes an image path (str) and returns
                            a dictionary containing prediction results
        """
        self.predict_function = predict_function
    
    def predict(self, image_path: str) -> Dict[str, Any]:
        """
        Call AI prediction function and validate results.
        
        This method orchestrates the complete inference workflow:
        1. Calls the external predict function with the image path
        2. Validates the result structure and values
        3. Handles any exceptions and wraps them in InferenceError
        
        Args:
            image_path: Absolute or relative path to the image file
        
        Returns:
            Dict containing validated prediction results with keys:
                - anomaly_score: float in range [0.0, 1.0]
                - status: one of "PASS", "REJECT", "REVIEW"
                - heatmap_path: str path to generated heatmap file
                - inference_time_ms: int positive milliseconds
        
        Raises:
            InferenceError: If prediction fails or results are invalid
        """
        try:
            # Call the external AI prediction function
            logger.info(f"Starting inference for image: {image_path}")
            result = self.predict_function(image_path)
            
            # Validate the prediction result
            self.validate_prediction_result(result)
            
            logger.info(f"Inference completed successfully for image: {image_path}")
            return result
            
        except InferenceError:
            # Re-raise InferenceError as-is
            raise
        except Exception as e:
            # Catch any other exceptions and wrap them
            error_msg = f"Inference failed for image {image_path}: {str(e)}"
            logger.error(error_msg)
            raise InferenceError(error_msg) from e
    
    def validate_prediction_result(self, result: Dict[str, Any]) -> None:
        """
        Validate prediction result structure and values.
        
        Performs comprehensive validation:
        1. Checks all required fields are present
        2. Validates anomaly_score is float in [0.0, 1.0]
        3. Validates status is one of PASS, REJECT, REVIEW
        4. Validates heatmap_path points to existing file
        5. Validates inference_time_ms is positive integer (converts float to int)
        
        Args:
            result: Dictionary containing prediction results
        
        Raises:
            InferenceError: If validation fails with descriptive message
        """
        # Check required fields are present
        required_fields = {'anomaly_score', 'status', 'heatmap_path', 'inference_time_ms'}
        missing_fields = required_fields - set(result.keys())
        if missing_fields:
            raise InferenceError(
                f"Prediction result missing required fields: {', '.join(missing_fields)}"
            )
        
        # Validate anomaly_score
        anomaly_score = result.get('anomaly_score')
        if not isinstance(anomaly_score, (int, float)):
            raise InferenceError(
                f"Invalid anomaly_score type: expected float, got {type(anomaly_score).__name__}"
            )
        if not (0.0 <= float(anomaly_score) <= 1.0):
            raise InferenceError(
                f"Invalid anomaly_score value: {anomaly_score}. Must be in range [0.0, 1.0]"
            )
        
        # Validate status
        status = result.get('status')
        valid_statuses = {'PASS', 'REJECT', 'REVIEW'}
        if status not in valid_statuses:
            raise InferenceError(
                f"Invalid status value: '{status}'. Must be one of {', '.join(valid_statuses)}"
            )
        
        # Validate heatmap_path
        heatmap_path = result.get('heatmap_path')
        if not isinstance(heatmap_path, str):
            raise InferenceError(
                f"Invalid heatmap_path type: expected str, got {type(heatmap_path).__name__}"
            )
        if not os.path.exists(heatmap_path):
            raise InferenceError(
                f"Heatmap file not found: {heatmap_path}"
            )
        
        # Validate and normalize inference_time_ms
        inference_time_ms = result.get('inference_time_ms')
        if inference_time_ms is None:
            # Default to 0 if None
            result['inference_time_ms'] = 0
            logger.warning("inference_time_ms was None, defaulting to 0")
        elif not isinstance(inference_time_ms, (int, float)):
            raise InferenceError(
                f"Invalid inference_time_ms type: expected int or float, got {type(inference_time_ms).__name__}"
            )
        else:
            # Convert float to int by rounding
            try:
                normalized_value = int(round(float(inference_time_ms)))
                result['inference_time_ms'] = normalized_value
                
                if normalized_value <= 0:
                    raise InferenceError(
                        f"Invalid inference_time_ms value: {inference_time_ms}. Must be positive"
                    )
            except (ValueError, OverflowError) as e:
                raise InferenceError(
                    f"Could not convert inference_time_ms to integer: {inference_time_ms}"
                ) from e


# Mock predict function for development and testing
def mock_predict_function(image_path: str) -> Dict[str, Any]:
    """
    Mock AI prediction function that returns sample results.
    
    This is a stub implementation for development and testing.
    In production, this would be replaced with the actual AI inference function.
    
    Args:
        image_path: Path to the image file to analyze
    
    Returns:
        Dict containing sample prediction results:
            - anomaly_score: Sample score of 0.75
            - status: Sample status of "REVIEW"
            - heatmap_path: Path to a mock heatmap (same as input image for now)
            - inference_time_ms: Sample inference time of 150ms
    """
    # For the mock, we'll just return sample data
    # In a real implementation, this would call the actual AI model
    
    # Generate a mock heatmap path (in production, AI would generate this)
    # For now, we'll use the same path as the input image
    heatmap_filename = f"heatmap_{os.path.basename(image_path)}"
    heatmap_path = os.path.join("results", heatmap_filename)
    
    # Create the heatmap file if it doesn't exist (mock)
    os.makedirs("results", exist_ok=True)
    if os.path.exists(image_path):
        # Copy the input image as the heatmap for now
        import shutil
        shutil.copy(image_path, heatmap_path)
    else:
        # Create an empty file if input doesn't exist
        with open(heatmap_path, 'w') as f:
            f.write("")
    
    return {
        "anomaly_score": 0.75,
        "status": "REVIEW",
        "heatmap_path": heatmap_path,
        "inference_time_ms": 150
    }
