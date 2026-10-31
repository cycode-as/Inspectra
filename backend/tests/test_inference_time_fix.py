"""
Integration test to verify inference_time_ms type conversion fix.

This test demonstrates that the inference service now correctly handles
float values for inference_time_ms by converting them to integers.
"""

import pytest
import tempfile
import os
from app.services.inference import InferenceService, InferenceError


class TestInferenceTimeConversionFix:
    """Test suite verifying the fix for inference_time_ms type mismatch."""
    
    def test_ai_model_returns_float_inference_time(self):
        """
        Test that simulates real-world scenario where AI model returns float.
        
        This verifies the fix for:
        "Invalid inference_time_ms type: expected int, got float"
        """
        # Create a temporary heatmap file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file.write(b"test heatmap")
        temp_file.close()
        
        try:
            # Mock AI prediction function that returns float inference_time
            def mock_ai_predict(image_path: str):
                return {
                    "anomaly_score": 0.75,
                    "status": "REVIEW",
                    "heatmap_path": temp_file.name,
                    "inference_time_ms": 152.3456  # Float from AI model
                }
            
            # Create inference service with mock function
            service = InferenceService(mock_ai_predict)
            
            # This should not raise InferenceError anymore
            result = service.predict("dummy_image.jpg")
            
            # Verify the result
            assert result is not None
            assert "inference_time_ms" in result
            
            # Verify conversion to integer
            assert isinstance(result["inference_time_ms"], int)
            assert result["inference_time_ms"] == 152  # Rounded from 152.3456
            
        finally:
            # Clean up
            os.unlink(temp_file.name)
    
    def test_handles_various_float_values(self):
        """Test conversion works with various float values."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file.write(b"test heatmap")
        temp_file.close()
        
        test_cases = [
            (100.1, 100),
            (100.5, 100),  # Banker's rounding
            (100.9, 101),
            (150.7, 151),
            (200.0, 200),
        ]
        
        try:
            for float_value, expected_int in test_cases:
                def mock_ai_predict(image_path: str):
                    return {
                        "anomaly_score": 0.5,
                        "status": "PASS",
                        "heatmap_path": temp_file.name,
                        "inference_time_ms": float_value
                    }
                
                service = InferenceService(mock_ai_predict)
                result = service.predict("test.jpg")
                
                assert isinstance(result["inference_time_ms"], int), \
                    f"Expected int, got {type(result['inference_time_ms'])}"
                assert result["inference_time_ms"] == expected_int, \
                    f"Expected {expected_int} from {float_value}, got {result['inference_time_ms']}"
        
        finally:
            os.unlink(temp_file.name)
    
    def test_handles_none_value_gracefully(self):
        """Test that None inference_time_ms defaults to 0."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file.write(b"test heatmap")
        temp_file.close()
        
        try:
            def mock_ai_predict(image_path: str):
                return {
                    "anomaly_score": 0.5,
                    "status": "PASS",
                    "heatmap_path": temp_file.name,
                    "inference_time_ms": None  # None value
                }
            
            service = InferenceService(mock_ai_predict)
            result = service.predict("test.jpg")
            
            # Should default to 0
            assert result["inference_time_ms"] == 0
            
        finally:
            os.unlink(temp_file.name)
    
    def test_still_rejects_invalid_types(self):
        """Test that non-numeric types are still rejected."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file.write(b"test heatmap")
        temp_file.close()
        
        try:
            def mock_ai_predict(image_path: str):
                return {
                    "anomaly_score": 0.5,
                    "status": "PASS",
                    "heatmap_path": temp_file.name,
                    "inference_time_ms": "not_a_number"  # Invalid string
                }
            
            service = InferenceService(mock_ai_predict)
            
            # Should raise InferenceError for invalid types
            with pytest.raises(InferenceError, match="Invalid inference_time_ms type"):
                service.predict("test.jpg")
            
        finally:
            os.unlink(temp_file.name)
