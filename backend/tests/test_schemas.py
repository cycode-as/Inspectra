"""
Unit Tests for Pydantic Schemas

Tests validation logic for InspectionCreate, InspectionResponse,
PredictionResult, and ErrorResponse models.
"""

import pytest
import os
import tempfile
from datetime import datetime
from pydantic import ValidationError
from app.schemas.inspection import (
    InspectionCreate,
    InspectionResponse,
    PredictionResult,
    ErrorResponse
)


class TestInspectionCreate:
    """Test suite for InspectionCreate schema validation."""
    
    def test_valid_inspection_create(self):
        """Test creation with valid data."""
        data = {
            "product_id": "PROD-123",
            "image_path": "/uploads/image.jpg",
            "heatmap_path": "/results/heatmap.jpg",
            "anomaly_score": 0.75,
            "status": "REVIEW",
            "inference_time_ms": 150
        }
        inspection = InspectionCreate(**data)
        assert inspection.product_id == "PROD-123"
        assert inspection.anomaly_score == 0.75
        assert inspection.status == "REVIEW"
        assert inspection.inference_time_ms == 150
    
    def test_anomaly_score_validation_valid_range(self):
        """Test anomaly_score accepts values in [0.0, 1.0] range."""
        for score in [0.0, 0.5, 1.0]:
            data = {
                "product_id": "PROD-123",
                "image_path": "/uploads/image.jpg",
                "heatmap_path": "/results/heatmap.jpg",
                "anomaly_score": score,
                "status": "PASS",
                "inference_time_ms": 100
            }
            inspection = InspectionCreate(**data)
            assert inspection.anomaly_score == score
    
    def test_anomaly_score_validation_below_range(self):
        """Test anomaly_score rejects values below 0.0."""
        data = {
            "product_id": "PROD-123",
            "image_path": "/uploads/image.jpg",
            "heatmap_path": "/results/heatmap.jpg",
            "anomaly_score": -0.1,
            "status": "PASS",
            "inference_time_ms": 100
        }
        with pytest.raises(ValidationError) as exc_info:
            InspectionCreate(**data)
        assert "anomaly_score" in str(exc_info.value)
    
    def test_anomaly_score_validation_above_range(self):
        """Test anomaly_score rejects values above 1.0."""
        data = {
            "product_id": "PROD-123",
            "image_path": "/uploads/image.jpg",
            "heatmap_path": "/results/heatmap.jpg",
            "anomaly_score": 1.5,
            "status": "PASS",
            "inference_time_ms": 100
        }
        with pytest.raises(ValidationError) as exc_info:
            InspectionCreate(**data)
        assert "anomaly_score" in str(exc_info.value)
    
    def test_status_validation_valid_values(self):
        """Test status accepts PASS, REJECT, REVIEW."""
        for status in ["PASS", "REJECT", "REVIEW"]:
            data = {
                "product_id": "PROD-123",
                "image_path": "/uploads/image.jpg",
                "heatmap_path": "/results/heatmap.jpg",
                "anomaly_score": 0.5,
                "status": status,
                "inference_time_ms": 100
            }
            inspection = InspectionCreate(**data)
            assert inspection.status == status
    
    def test_status_validation_invalid_value(self):
        """Test status rejects invalid values."""
        data = {
            "product_id": "PROD-123",
            "image_path": "/uploads/image.jpg",
            "heatmap_path": "/results/heatmap.jpg",
            "anomaly_score": 0.5,
            "status": "INVALID",
            "inference_time_ms": 100
        }
        with pytest.raises(ValidationError) as exc_info:
            InspectionCreate(**data)
        assert "status" in str(exc_info.value).lower()
    
    def test_inference_time_validation_positive(self):
        """Test inference_time_ms accepts positive integers."""
        data = {
            "product_id": "PROD-123",
            "image_path": "/uploads/image.jpg",
            "heatmap_path": "/results/heatmap.jpg",
            "anomaly_score": 0.5,
            "status": "PASS",
            "inference_time_ms": 150
        }
        inspection = InspectionCreate(**data)
        assert inspection.inference_time_ms == 150
    
    def test_inference_time_validation_zero(self):
        """Test inference_time_ms rejects zero."""
        data = {
            "product_id": "PROD-123",
            "image_path": "/uploads/image.jpg",
            "heatmap_path": "/results/heatmap.jpg",
            "anomaly_score": 0.5,
            "status": "PASS",
            "inference_time_ms": 0
        }
        with pytest.raises(ValidationError) as exc_info:
            InspectionCreate(**data)
        assert "inference_time_ms" in str(exc_info.value)
    
    def test_inference_time_validation_negative(self):
        """Test inference_time_ms rejects negative values."""
        data = {
            "product_id": "PROD-123",
            "image_path": "/uploads/image.jpg",
            "heatmap_path": "/results/heatmap.jpg",
            "anomaly_score": 0.5,
            "status": "PASS",
            "inference_time_ms": -10
        }
        with pytest.raises(ValidationError) as exc_info:
            InspectionCreate(**data)
        assert "inference_time_ms" in str(exc_info.value)
    
    def test_product_id_min_length(self):
        """Test product_id requires at least 1 character."""
        data = {
            "product_id": "",
            "image_path": "/uploads/image.jpg",
            "heatmap_path": "/results/heatmap.jpg",
            "anomaly_score": 0.5,
            "status": "PASS",
            "inference_time_ms": 100
        }
        with pytest.raises(ValidationError) as exc_info:
            InspectionCreate(**data)
        assert "product_id" in str(exc_info.value)


class TestInspectionResponse:
    """Test suite for InspectionResponse schema validation."""
    
    def test_valid_inspection_response(self):
        """Test creation with valid data."""
        data = {
            "id": 1,
            "product_id": "PROD-123",
            "image_url": "http://localhost:8000/uploads/image.jpg",
            "heatmap_url": "http://localhost:8000/results/heatmap.jpg",
            "anomaly_score": 0.85,
            "status": "REJECT",
            "inference_time_ms": 200,
            "created_at": datetime.now()
        }
        response = InspectionResponse(**data)
        assert response.id == 1
        assert response.product_id == "PROD-123"
        assert response.status == "REJECT"
    
    def test_orm_mode_configuration(self):
        """Test that orm_mode is properly configured."""
        # This verifies the model_config with from_attributes=True
        assert InspectionResponse.model_config.get("from_attributes") is True


class TestPredictionResult:
    """Test suite for PredictionResult schema validation."""
    
    def test_valid_prediction_result_with_existing_file(self):
        """Test creation with valid data and existing heatmap file."""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jpg') as f:
            temp_path = f.name
            f.write("test")
        
        try:
            data = {
                "anomaly_score": 0.65,
                "status": "REVIEW",
                "heatmap_path": temp_path,
                "inference_time_ms": 175
            }
            result = PredictionResult(**data)
            assert result.anomaly_score == 0.65
            assert result.status == "REVIEW"
            assert result.heatmap_path == temp_path
            assert result.inference_time_ms == 175
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_heatmap_path_validation_file_exists(self):
        """Test heatmap_path validator accepts existing files."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jpg') as f:
            temp_path = f.name
            f.write("test")
        
        try:
            data = {
                "anomaly_score": 0.5,
                "status": "PASS",
                "heatmap_path": temp_path,
                "inference_time_ms": 100
            }
            result = PredictionResult(**data)
            assert result.heatmap_path == temp_path
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_heatmap_path_validation_file_not_exists(self):
        """Test heatmap_path validator rejects non-existent files."""
        data = {
            "anomaly_score": 0.5,
            "status": "PASS",
            "heatmap_path": "/nonexistent/path/to/heatmap.jpg",
            "inference_time_ms": 100
        }
        with pytest.raises(ValidationError) as exc_info:
            PredictionResult(**data)
        assert "heatmap_path" in str(exc_info.value).lower()
        assert "not found" in str(exc_info.value).lower()
    
    def test_anomaly_score_validation_boundary_values(self):
        """Test anomaly_score validation at boundaries."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jpg') as f:
            temp_path = f.name
            f.write("test")
        
        try:
            # Test boundary values 0.0 and 1.0
            for score in [0.0, 1.0]:
                data = {
                    "anomaly_score": score,
                    "status": "PASS",
                    "heatmap_path": temp_path,
                    "inference_time_ms": 100
                }
                result = PredictionResult(**data)
                assert result.anomaly_score == score
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_status_validation_all_valid_values(self):
        """Test status validation accepts all valid values."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jpg') as f:
            temp_path = f.name
            f.write("test")
        
        try:
            for status in ["PASS", "REJECT", "REVIEW"]:
                data = {
                    "anomaly_score": 0.5,
                    "status": status,
                    "heatmap_path": temp_path,
                    "inference_time_ms": 100
                }
                result = PredictionResult(**data)
                assert result.status == status
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestErrorResponse:
    """Test suite for ErrorResponse schema validation."""
    
    def test_error_response_with_detail(self):
        """Test creation with error and detail."""
        error = ErrorResponse(
            error="Validation failed",
            detail="File format not supported"
        )
        assert error.error == "Validation failed"
        assert error.detail == "File format not supported"
    
    def test_error_response_without_detail(self):
        """Test creation with error only."""
        error = ErrorResponse(error="Internal server error")
        assert error.error == "Internal server error"
        assert error.detail is None
    
    def test_error_response_minimal(self):
        """Test creation with minimal required fields."""
        error = ErrorResponse(error="Error occurred")
        assert error.error == "Error occurred"
