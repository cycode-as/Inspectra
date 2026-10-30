"""
Unit tests for InferenceService.

Tests inference service integration, result validation, and error handling.
"""

import pytest
import os
import tempfile
from typing import Dict, Any
from app.services.inference import InferenceService, InferenceError, mock_predict_function


class TestInferenceService:
    """Test suite for InferenceService class."""
    
    def create_mock_predict_function(self, return_value: Dict[str, Any]):
        """
        Helper to create a mock predict function that returns a specific value.
        
        Args:
            return_value: Dictionary to return from the mock function
        
        Returns:
            Callable that returns the specified value
        """
        def mock_predict(image_path: str) -> Dict[str, Any]:
            return return_value
        return mock_predict
    
    def create_mock_predict_function_with_exception(self, exception: Exception):
        """
        Helper to create a mock predict function that raises an exception.
        
        Args:
            exception: Exception to raise
        
        Returns:
            Callable that raises the specified exception
        """
        def mock_predict(image_path: str) -> Dict[str, Any]:
            raise exception
        return mock_predict
    
    def create_temp_file(self) -> str:
        """
        Helper to create a temporary file for testing.
        
        Returns:
            str: Path to the temporary file
        """
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            return f.name
    
    def test_predict_with_valid_result(self):
        """Test predict() with valid prediction result."""
        temp_file = self.create_temp_file()
        try:
            valid_result = {
                "anomaly_score": 0.75,
                "status": "REVIEW",
                "heatmap_path": temp_file,
                "inference_time_ms": 150
            }
            
            mock_func = self.create_mock_predict_function(valid_result)
            service = InferenceService(mock_func)
            
            result = service.predict("test_image.jpg")
            
            assert result == valid_result
            assert result["anomaly_score"] == 0.75
            assert result["status"] == "REVIEW"
            assert result["heatmap_path"] == temp_file
            assert result["inference_time_ms"] == 150
        finally:
            os.unlink(temp_file)
    
    def test_predict_calls_predict_function_with_image_path(self):
        """Test predict() calls the predict function with correct image path."""
        temp_file = self.create_temp_file()
        try:
            valid_result = {
                "anomaly_score": 0.5,
                "status": "PASS",
                "heatmap_path": temp_file,
                "inference_time_ms": 100
            }
            
            called_with = []
            def tracking_mock(image_path: str) -> Dict[str, Any]:
                called_with.append(image_path)
                return valid_result
            
            service = InferenceService(tracking_mock)
            service.predict("path/to/image.jpg")
            
            assert called_with == ["path/to/image.jpg"]
        finally:
            os.unlink(temp_file)
    
    def test_predict_with_exception_raises_inference_error(self):
        """Test predict() wraps exceptions in InferenceError."""
        mock_func = self.create_mock_predict_function_with_exception(
            RuntimeError("AI model failed")
        )
        service = InferenceService(mock_func)
        
        with pytest.raises(InferenceError, match="Inference failed for image"):
            service.predict("test_image.jpg")
    
    def test_predict_with_exception_includes_original_error_message(self):
        """Test InferenceError includes original exception message."""
        mock_func = self.create_mock_predict_function_with_exception(
            ValueError("Invalid input tensor shape")
        )
        service = InferenceService(mock_func)
        
        with pytest.raises(InferenceError, match="Invalid input tensor shape"):
            service.predict("test_image.jpg")
    
    def test_predict_with_validation_error_raises_inference_error(self):
        """Test predict() raises InferenceError when validation fails."""
        invalid_result = {
            "anomaly_score": 1.5,  # Invalid: > 1.0
            "status": "PASS",
            "heatmap_path": "/nonexistent/path.jpg",
            "inference_time_ms": 100
        }
        
        mock_func = self.create_mock_predict_function(invalid_result)
        service = InferenceService(mock_func)
        
        with pytest.raises(InferenceError):
            service.predict("test_image.jpg")
    
    def test_validate_prediction_result_with_valid_data(self):
        """Test validate_prediction_result() accepts valid data."""
        temp_file = self.create_temp_file()
        try:
            valid_result = {
                "anomaly_score": 0.85,
                "status": "REJECT",
                "heatmap_path": temp_file,
                "inference_time_ms": 200
            }
            
            service = InferenceService(lambda x: {})
            service.validate_prediction_result(valid_result)  # Should not raise
        finally:
            os.unlink(temp_file)
    
    def test_validate_prediction_result_with_missing_field(self):
        """Test validation fails when required field is missing."""
        temp_file = self.create_temp_file()
        try:
            incomplete_result = {
                "anomaly_score": 0.5,
                "status": "PASS",
                "heatmap_path": temp_file
                # Missing inference_time_ms
            }
            
            service = InferenceService(lambda x: {})
            
            with pytest.raises(InferenceError, match="missing required fields"):
                service.validate_prediction_result(incomplete_result)
        finally:
            os.unlink(temp_file)
    
    def test_validate_prediction_result_with_multiple_missing_fields(self):
        """Test validation lists all missing fields."""
        service = InferenceService(lambda x: {})
        
        incomplete_result = {
            "anomaly_score": 0.5
            # Missing status, heatmap_path, inference_time_ms
        }
        
        with pytest.raises(InferenceError) as exc_info:
            service.validate_prediction_result(incomplete_result)
        
        error_msg = str(exc_info.value)
        assert "status" in error_msg
        assert "heatmap_path" in error_msg
        assert "inference_time_ms" in error_msg
    
    def test_validate_anomaly_score_accepts_valid_range(self):
        """Test validation accepts anomaly_score in [0.0, 1.0] range."""
        temp_file = self.create_temp_file()
        try:
            service = InferenceService(lambda x: {})
            
            # Test boundary values
            for score in [0.0, 0.5, 1.0]:
                result = {
                    "anomaly_score": score,
                    "status": "PASS",
                    "heatmap_path": temp_file,
                    "inference_time_ms": 100
                }
                service.validate_prediction_result(result)  # Should not raise
        finally:
            os.unlink(temp_file)
    
    def test_validate_anomaly_score_rejects_negative_value(self):
        """Test validation rejects negative anomaly_score."""
        temp_file = self.create_temp_file()
        try:
            invalid_result = {
                "anomaly_score": -0.1,
                "status": "PASS",
                "heatmap_path": temp_file,
                "inference_time_ms": 100
            }
            
            service = InferenceService(lambda x: {})
            
            with pytest.raises(InferenceError, match="Invalid anomaly_score value"):
                service.validate_prediction_result(invalid_result)
        finally:
            os.unlink(temp_file)
    
    def test_validate_anomaly_score_rejects_value_above_one(self):
        """Test validation rejects anomaly_score > 1.0."""
        temp_file = self.create_temp_file()
        try:
            invalid_result = {
                "anomaly_score": 1.5,
                "status": "PASS",
                "heatmap_path": temp_file,
                "inference_time_ms": 100
            }
            
            service = InferenceService(lambda x: {})
            
            with pytest.raises(InferenceError, match="Invalid anomaly_score value"):
                service.validate_prediction_result(invalid_result)
        finally:
            os.unlink(temp_file)
    
    def test_validate_anomaly_score_accepts_integer(self):
        """Test validation accepts integer anomaly_score (0 or 1)."""
        temp_file = self.create_temp_file()
        try:
            service = InferenceService(lambda x: {})
            
            for score in [0, 1]:
                result = {
                    "anomaly_score": score,
                    "status": "PASS",
                    "heatmap_path": temp_file,
                    "inference_time_ms": 100
                }
                service.validate_prediction_result(result)  # Should not raise
        finally:
            os.unlink(temp_file)
    
    def test_validate_anomaly_score_rejects_non_numeric_type(self):
        """Test validation rejects non-numeric anomaly_score."""
        temp_file = self.create_temp_file()
        try:
            invalid_result = {
                "anomaly_score": "0.5",  # String instead of float
                "status": "PASS",
                "heatmap_path": temp_file,
                "inference_time_ms": 100
            }
            
            service = InferenceService(lambda x: {})
            
            with pytest.raises(InferenceError, match="Invalid anomaly_score type"):
                service.validate_prediction_result(invalid_result)
        finally:
            os.unlink(temp_file)
    
    def test_validate_status_accepts_pass(self):
        """Test validation accepts status 'PASS'."""
        temp_file = self.create_temp_file()
        try:
            result = {
                "anomaly_score": 0.2,
                "status": "PASS",
                "heatmap_path": temp_file,
                "inference_time_ms": 100
            }
            
            service = InferenceService(lambda x: {})
            service.validate_prediction_result(result)  # Should not raise
        finally:
            os.unlink(temp_file)
    
    def test_validate_status_accepts_reject(self):
        """Test validation accepts status 'REJECT'."""
        temp_file = self.create_temp_file()
        try:
            result = {
                "anomaly_score": 0.9,
                "status": "REJECT",
                "heatmap_path": temp_file,
                "inference_time_ms": 100
            }
            
            service = InferenceService(lambda x: {})
            service.validate_prediction_result(result)  # Should not raise
        finally:
            os.unlink(temp_file)
    
    def test_validate_status_accepts_review(self):
        """Test validation accepts status 'REVIEW'."""
        temp_file = self.create_temp_file()
        try:
            result = {
                "anomaly_score": 0.5,
                "status": "REVIEW",
                "heatmap_path": temp_file,
                "inference_time_ms": 100
            }
            
            service = InferenceService(lambda x: {})
            service.validate_prediction_result(result)  # Should not raise
        finally:
            os.unlink(temp_file)
    
    def test_validate_status_rejects_invalid_value(self):
        """Test validation rejects invalid status value."""
        temp_file = self.create_temp_file()
        try:
            invalid_result = {
                "anomaly_score": 0.5,
                "status": "UNKNOWN",
                "heatmap_path": temp_file,
                "inference_time_ms": 100
            }
            
            service = InferenceService(lambda x: {})
            
            with pytest.raises(InferenceError, match="Invalid status value"):
                service.validate_prediction_result(invalid_result)
        finally:
            os.unlink(temp_file)
    
    def test_validate_status_rejects_lowercase(self):
        """Test validation rejects lowercase status values."""
        temp_file = self.create_temp_file()
        try:
            invalid_result = {
                "anomaly_score": 0.5,
                "status": "pass",  # Should be "PASS"
                "heatmap_path": temp_file,
                "inference_time_ms": 100
            }
            
            service = InferenceService(lambda x: {})
            
            with pytest.raises(InferenceError, match="Invalid status value"):
                service.validate_prediction_result(invalid_result)
        finally:
            os.unlink(temp_file)
    
    def test_validate_heatmap_path_rejects_nonexistent_file(self):
        """Test validation rejects heatmap_path to nonexistent file."""
        invalid_result = {
            "anomaly_score": 0.5,
            "status": "PASS",
            "heatmap_path": "/nonexistent/path/to/heatmap.jpg",
            "inference_time_ms": 100
        }
        
        service = InferenceService(lambda x: {})
        
        with pytest.raises(InferenceError, match="Heatmap file not found"):
            service.validate_prediction_result(invalid_result)
    
    def test_validate_heatmap_path_accepts_existing_file(self):
        """Test validation accepts heatmap_path to existing file."""
        temp_file = self.create_temp_file()
        try:
            result = {
                "anomaly_score": 0.5,
                "status": "PASS",
                "heatmap_path": temp_file,
                "inference_time_ms": 100
            }
            
            service = InferenceService(lambda x: {})
            service.validate_prediction_result(result)  # Should not raise
        finally:
            os.unlink(temp_file)
    
    def test_validate_heatmap_path_rejects_non_string(self):
        """Test validation rejects non-string heatmap_path."""
        invalid_result = {
            "anomaly_score": 0.5,
            "status": "PASS",
            "heatmap_path": 12345,  # Should be string
            "inference_time_ms": 100
        }
        
        service = InferenceService(lambda x: {})
        
        with pytest.raises(InferenceError, match="Invalid heatmap_path type"):
            service.validate_prediction_result(invalid_result)
    
    def test_validate_inference_time_ms_accepts_positive_integer(self):
        """Test validation accepts positive inference_time_ms."""
        temp_file = self.create_temp_file()
        try:
            result = {
                "anomaly_score": 0.5,
                "status": "PASS",
                "heatmap_path": temp_file,
                "inference_time_ms": 150
            }
            
            service = InferenceService(lambda x: {})
            service.validate_prediction_result(result)  # Should not raise
        finally:
            os.unlink(temp_file)
    
    def test_validate_inference_time_ms_rejects_zero(self):
        """Test validation rejects inference_time_ms of zero."""
        temp_file = self.create_temp_file()
        try:
            invalid_result = {
                "anomaly_score": 0.5,
                "status": "PASS",
                "heatmap_path": temp_file,
                "inference_time_ms": 0
            }
            
            service = InferenceService(lambda x: {})
            
            with pytest.raises(InferenceError, match="Must be positive"):
                service.validate_prediction_result(invalid_result)
        finally:
            os.unlink(temp_file)
    
    def test_validate_inference_time_ms_rejects_negative(self):
        """Test validation rejects negative inference_time_ms."""
        temp_file = self.create_temp_file()
        try:
            invalid_result = {
                "anomaly_score": 0.5,
                "status": "PASS",
                "heatmap_path": temp_file,
                "inference_time_ms": -100
            }
            
            service = InferenceService(lambda x: {})
            
            with pytest.raises(InferenceError, match="Must be positive"):
                service.validate_prediction_result(invalid_result)
        finally:
            os.unlink(temp_file)
    
    def test_validate_inference_time_ms_rejects_non_integer(self):
        """Test validation rejects non-integer inference_time_ms."""
        temp_file = self.create_temp_file()
        try:
            invalid_result = {
                "anomaly_score": 0.5,
                "status": "PASS",
                "heatmap_path": temp_file,
                "inference_time_ms": 150.5  # Should be int
            }
            
            service = InferenceService(lambda x: {})
            
            with pytest.raises(InferenceError, match="Invalid inference_time_ms type"):
                service.validate_prediction_result(invalid_result)
        finally:
            os.unlink(temp_file)


class TestMockPredictFunction:
    """Test suite for mock_predict_function."""
    
    def test_mock_predict_function_returns_valid_structure(self):
        """Test mock function returns valid prediction structure."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file.write(b"test image")
        temp_file.close()
        
        try:
            result = mock_predict_function(temp_file.name)
            
            assert "anomaly_score" in result
            assert "status" in result
            assert "heatmap_path" in result
            assert "inference_time_ms" in result
        finally:
            os.unlink(temp_file.name)
            # Clean up heatmap if created
            heatmap_path = os.path.join("results", f"heatmap_{os.path.basename(temp_file.name)}")
            if os.path.exists(heatmap_path):
                os.unlink(heatmap_path)
    
    def test_mock_predict_function_creates_heatmap_file(self):
        """Test mock function creates a heatmap file."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file.write(b"test image")
        temp_file.close()
        
        try:
            result = mock_predict_function(temp_file.name)
            heatmap_path = result["heatmap_path"]
            
            assert os.path.exists(heatmap_path)
        finally:
            os.unlink(temp_file.name)
            if "heatmap_path" in result and os.path.exists(result["heatmap_path"]):
                os.unlink(result["heatmap_path"])
    
    def test_mock_predict_function_with_inference_service(self):
        """Test mock function works with InferenceService."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file.write(b"test image")
        temp_file.close()
        
        try:
            service = InferenceService(mock_predict_function)
            result = service.predict(temp_file.name)
            
            # Should not raise and return valid result
            assert result["anomaly_score"] == 0.75
            assert result["status"] == "REVIEW"
            assert result["inference_time_ms"] == 150
        finally:
            os.unlink(temp_file.name)
            if "heatmap_path" in result and os.path.exists(result["heatmap_path"]):
                os.unlink(result["heatmap_path"])
