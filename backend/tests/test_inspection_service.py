"""
Unit Tests for Inspection Service

Tests the inspection service business logic layer including:
- Complete inspection workflow orchestration
- Integration with inference service, repository, and storage
- Transaction handling and error recovery
- Error handling for various failure scenarios
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.services.inspection import InspectionService, InspectionServiceError
from app.services.inference import InferenceService, InferenceError
from app.services.storage import FileStorageService
from app.schemas.inspection import InspectionCreate
from app.models.inspection import Inspection


class TestInspectionServiceInitialization:
    """Test InspectionService initialization."""
    
    def test_init_with_all_dependencies(self):
        """Test initialization with all dependencies provided."""
        db_session = Mock(spec=Session)
        inference_service = Mock(spec=InferenceService)
        storage_service = Mock(spec=FileStorageService)
        
        service = InspectionService(
            db=db_session,
            inference_service=inference_service,
            storage_service=storage_service
        )
        
        assert service.db == db_session
        assert service.inference_service == inference_service
        assert service.storage_service == storage_service
        assert service.repository is not None
    
    def test_init_creates_default_storage_service(self):
        """Test that default storage service is created if not provided."""
        db_session = Mock(spec=Session)
        inference_service = Mock(spec=InferenceService)
        
        service = InspectionService(
            db=db_session,
            inference_service=inference_service
        )
        
        assert service.storage_service is not None
        assert isinstance(service.storage_service, FileStorageService)


class TestProcessInspection:
    """Test the complete inspection workflow."""
    
    def test_process_inspection_success(self):
        """Test successful inspection workflow from image to database record."""
        # Arrange
        db_session = Mock(spec=Session)
        inference_service = Mock(spec=InferenceService)
        storage_service = Mock(spec=FileStorageService)
        
        # Mock inference result
        mock_prediction = {
            'anomaly_score': 0.75,
            'status': 'REVIEW',
            'heatmap_path': 'results/heatmap.jpg',
            'inference_time_ms': 150
        }
        inference_service.predict.return_value = mock_prediction
        
        # Mock database record
        mock_inspection = Inspection(
            id=1,
            product_id='PROD-123',
            image_path='uploads/image.jpg',
            heatmap_path='results/heatmap.jpg',
            anomaly_score=0.75,
            status='REVIEW',
            inference_time_ms=150
        )
        
        service = InspectionService(
            db=db_session,
            inference_service=inference_service,
            storage_service=storage_service
        )
        
        # Mock repository create method
        service.repository.create = Mock(return_value=mock_inspection)
        
        # Act
        result = service.process_inspection(
            image_path='uploads/image.jpg',
            product_id='PROD-123'
        )
        
        # Assert
        assert result == mock_inspection
        inference_service.predict.assert_called_once_with('uploads/image.jpg')
        service.repository.create.assert_called_once()
        
        # Verify the inspection data passed to repository
        call_args = service.repository.create.call_args[0][0]
        assert call_args.product_id == 'PROD-123'
        assert call_args.image_path == 'uploads/image.jpg'
        assert call_args.heatmap_path == 'results/heatmap.jpg'
        assert call_args.anomaly_score == 0.75
        assert call_args.status == 'REVIEW'
        assert call_args.inference_time_ms == 150
    
    def test_process_inspection_with_pass_status(self):
        """Test inspection workflow with PASS status."""
        # Arrange
        db_session = Mock(spec=Session)
        inference_service = Mock(spec=InferenceService)
        
        mock_prediction = {
            'anomaly_score': 0.15,
            'status': 'PASS',
            'heatmap_path': 'results/heatmap.jpg',
            'inference_time_ms': 100
        }
        inference_service.predict.return_value = mock_prediction
        
        mock_inspection = Inspection(
            id=2,
            product_id='PROD-456',
            image_path='uploads/image2.jpg',
            heatmap_path='results/heatmap.jpg',
            anomaly_score=0.15,
            status='PASS',
            inference_time_ms=100
        )
        
        service = InspectionService(
            db=db_session,
            inference_service=inference_service
        )
        service.repository.create = Mock(return_value=mock_inspection)
        
        # Act
        result = service.process_inspection(
            image_path='uploads/image2.jpg',
            product_id='PROD-456'
        )
        
        # Assert
        assert result.status == 'PASS'
        assert result.anomaly_score == 0.15
    
    def test_process_inspection_with_reject_status(self):
        """Test inspection workflow with REJECT status."""
        # Arrange
        db_session = Mock(spec=Session)
        inference_service = Mock(spec=InferenceService)
        
        mock_prediction = {
            'anomaly_score': 0.95,
            'status': 'REJECT',
            'heatmap_path': 'results/heatmap.jpg',
            'inference_time_ms': 200
        }
        inference_service.predict.return_value = mock_prediction
        
        mock_inspection = Inspection(
            id=3,
            product_id='PROD-789',
            image_path='uploads/image3.jpg',
            heatmap_path='results/heatmap.jpg',
            anomaly_score=0.95,
            status='REJECT',
            inference_time_ms=200
        )
        
        service = InspectionService(
            db=db_session,
            inference_service=inference_service
        )
        service.repository.create = Mock(return_value=mock_inspection)
        
        # Act
        result = service.process_inspection(
            image_path='uploads/image3.jpg',
            product_id='PROD-789'
        )
        
        # Assert
        assert result.status == 'REJECT'
        assert result.anomaly_score == 0.95


class TestProcessInspectionErrorHandling:
    """Test error handling in inspection workflow."""
    
    def test_process_inspection_handles_inference_error(self):
        """Test that inference errors are properly handled and wrapped."""
        # Arrange
        db_session = Mock(spec=Session)
        inference_service = Mock(spec=InferenceService)
        
        # Mock inference to raise error
        inference_service.predict.side_effect = InferenceError("AI prediction failed")
        
        service = InspectionService(
            db=db_session,
            inference_service=inference_service
        )
        
        # Act & Assert
        with pytest.raises(InspectionServiceError) as exc_info:
            service.process_inspection(
                image_path='uploads/image.jpg',
                product_id='PROD-123'
            )
        
        assert "Inference failed" in str(exc_info.value)
        # Verify inference was called
        inference_service.predict.assert_called_once()
    
    def test_process_inspection_handles_database_error(self):
        """Test that database errors are properly handled and wrapped."""
        # Arrange
        db_session = Mock(spec=Session)
        inference_service = Mock(spec=InferenceService)
        
        mock_prediction = {
            'anomaly_score': 0.75,
            'status': 'REVIEW',
            'heatmap_path': 'results/heatmap.jpg',
            'inference_time_ms': 150
        }
        inference_service.predict.return_value = mock_prediction
        
        service = InspectionService(
            db=db_session,
            inference_service=inference_service
        )
        
        # Mock repository to raise database error
        service.repository.create = Mock(
            side_effect=SQLAlchemyError("Database connection lost")
        )
        
        # Act & Assert
        with pytest.raises(InspectionServiceError) as exc_info:
            service.process_inspection(
                image_path='uploads/image.jpg',
                product_id='PROD-123'
            )
        
        assert "Database error" in str(exc_info.value)
        # Inference should have been called
        inference_service.predict.assert_called_once()
    
    def test_process_inspection_handles_unexpected_error(self):
        """Test that unexpected errors are properly handled and wrapped."""
        # Arrange
        db_session = Mock(spec=Session)
        inference_service = Mock(spec=InferenceService)
        
        # Mock inference to raise unexpected error
        inference_service.predict.side_effect = RuntimeError("Unexpected error")
        
        service = InspectionService(
            db=db_session,
            inference_service=inference_service
        )
        
        # Act & Assert
        with pytest.raises(InspectionServiceError) as exc_info:
            service.process_inspection(
                image_path='uploads/image.jpg',
                product_id='PROD-123'
            )
        
        assert "Unexpected error" in str(exc_info.value)


class TestGetInspectionById:
    """Test retrieving single inspection by ID."""
    
    def test_get_inspection_by_id_success(self):
        """Test successful retrieval of inspection by ID."""
        # Arrange
        db_session = Mock(spec=Session)
        inference_service = Mock(spec=InferenceService)
        
        mock_inspection = Inspection(
            id=1,
            product_id='PROD-123',
            image_path='uploads/image.jpg',
            heatmap_path='results/heatmap.jpg',
            anomaly_score=0.75,
            status='REVIEW',
            inference_time_ms=150
        )
        
        service = InspectionService(
            db=db_session,
            inference_service=inference_service
        )
        service.repository.get_by_id = Mock(return_value=mock_inspection)
        
        # Act
        result = service.get_inspection_by_id(1)
        
        # Assert
        assert result == mock_inspection
        service.repository.get_by_id.assert_called_once_with(1)
    
    def test_get_inspection_by_id_not_found(self):
        """Test retrieval when inspection doesn't exist."""
        # Arrange
        db_session = Mock(spec=Session)
        inference_service = Mock(spec=InferenceService)
        
        service = InspectionService(
            db=db_session,
            inference_service=inference_service
        )
        service.repository.get_by_id = Mock(return_value=None)
        
        # Act
        result = service.get_inspection_by_id(999)
        
        # Assert
        assert result is None
        service.repository.get_by_id.assert_called_once_with(999)
    
    def test_get_inspection_by_id_handles_database_error(self):
        """Test that database errors are properly handled."""
        # Arrange
        db_session = Mock(spec=Session)
        inference_service = Mock(spec=InferenceService)
        
        service = InspectionService(
            db=db_session,
            inference_service=inference_service
        )
        service.repository.get_by_id = Mock(
            side_effect=SQLAlchemyError("Database error")
        )
        
        # Act & Assert
        with pytest.raises(InspectionServiceError) as exc_info:
            service.get_inspection_by_id(1)
        
        assert "Error retrieving inspection" in str(exc_info.value)


class TestGetAllInspections:
    """Test retrieving all inspections."""
    
    def test_get_all_inspections_success(self):
        """Test successful retrieval of all inspections."""
        # Arrange
        db_session = Mock(spec=Session)
        inference_service = Mock(spec=InferenceService)
        
        mock_inspections = [
            Inspection(id=1, product_id='PROD-1', image_path='img1.jpg',
                      heatmap_path='heat1.jpg', anomaly_score=0.5,
                      status='PASS', inference_time_ms=100),
            Inspection(id=2, product_id='PROD-2', image_path='img2.jpg',
                      heatmap_path='heat2.jpg', anomaly_score=0.8,
                      status='REVIEW', inference_time_ms=150),
        ]
        
        service = InspectionService(
            db=db_session,
            inference_service=inference_service
        )
        service.repository.get_all = Mock(return_value=mock_inspections)
        
        # Act
        result = service.get_all_inspections()
        
        # Assert
        assert result == mock_inspections
        assert len(result) == 2
        service.repository.get_all.assert_called_once()
    
    def test_get_all_inspections_empty(self):
        """Test retrieval when no inspections exist."""
        # Arrange
        db_session = Mock(spec=Session)
        inference_service = Mock(spec=InferenceService)
        
        service = InspectionService(
            db=db_session,
            inference_service=inference_service
        )
        service.repository.get_all = Mock(return_value=[])
        
        # Act
        result = service.get_all_inspections()
        
        # Assert
        assert result == []
        assert len(result) == 0
    
    def test_get_all_inspections_handles_database_error(self):
        """Test that database errors are properly handled."""
        # Arrange
        db_session = Mock(spec=Session)
        inference_service = Mock(spec=InferenceService)
        
        service = InspectionService(
            db=db_session,
            inference_service=inference_service
        )
        service.repository.get_all = Mock(
            side_effect=SQLAlchemyError("Database error")
        )
        
        # Act & Assert
        with pytest.raises(InspectionServiceError) as exc_info:
            service.get_all_inspections()
        
        assert "Error retrieving all inspections" in str(exc_info.value)


# Feature: inspectra-fastapi-backend, Task 7: Implement business logic service layer
# Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.9

