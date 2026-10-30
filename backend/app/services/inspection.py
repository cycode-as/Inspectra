"""
Inspection Service Module

Business logic service layer that orchestrates the complete inspection workflow.
Coordinates between inference service, database repository, and file storage.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.services.inference import InferenceService, InferenceError
from app.services.storage import FileStorageService
from app.repositories.inspection import InspectionRepository
from app.schemas.inspection import InspectionCreate
from app.models.inspection import Inspection

# Configure logging
logger = logging.getLogger(__name__)


class InspectionServiceError(Exception):
    """Exception raised when inspection service operations fail."""
    pass


class InspectionService:
    """
    Service for orchestrating complete inspection workflows.
    
    Responsibilities:
    - Coordinate between inference service, database, and file storage
    - Orchestrate complete inspection workflow from image to database record
    - Handle transactions and error recovery
    - Provide clean interface for API layer
    
    Attributes:
        db (Session): SQLAlchemy database session
        inference_service (InferenceService): Service for AI prediction
        storage_service (FileStorageService): Service for file operations
        repository (InspectionRepository): Repository for database operations
    """
    
    def __init__(
        self,
        db: Session,
        inference_service: InferenceService,
        storage_service: Optional[FileStorageService] = None
    ):
        """
        Initialize the inspection service with required dependencies.
        
        Args:
            db: SQLAlchemy database session for transaction management
            inference_service: Service for calling AI prediction function
            storage_service: Service for file operations (creates default if None)
        """
        self.db = db
        self.inference_service = inference_service
        self.storage_service = storage_service or FileStorageService()
        self.repository = InspectionRepository(db)
    
    def process_inspection(
        self,
        image_path: str,
        product_id: str
    ) -> Inspection:
        """
        Process a complete inspection workflow.
        
        This method orchestrates the entire inspection process:
        1. Call inference service to get AI prediction for the image
        2. Validate inference results (handled by InferenceService)
        3. Create inspection record in database using repository
        4. Return the created inspection record with all fields populated
        
        The method implements transaction handling to ensure data consistency.
        If any step fails, the database transaction is rolled back and an
        error is raised with cleanup as needed.
        
        Args:
            image_path: Path to the uploaded image file (relative or absolute)
            product_id: Product identifier from the upload form data
            
        Returns:
            Inspection: Created inspection record with all fields populated,
                       including auto-generated id and created_at timestamp
            
        Raises:
            InspectionServiceError: If any step of the inspection process fails
                                   (wraps underlying errors with descriptive message)
        
        Example:
            >>> service = InspectionService(db, inference_service)
            >>> inspection = service.process_inspection(
            ...     image_path="uploads/image.jpg",
            ...     product_id="PROD-123"
            ... )
            >>> print(f"Inspection {inspection.id} created with status {inspection.status}")
            Inspection 1 created with status REVIEW
        """
        # Track resources for cleanup on failure
        created_record = None
        
        try:
            # Step 1: Call inference service to analyze the image
            logger.info(
                f"Starting inspection workflow: product_id={product_id}, "
                f"image_path={image_path}"
            )
            
            prediction_result = self.inference_service.predict(image_path)
            
            logger.info(
                f"Inference completed: anomaly_score={prediction_result['anomaly_score']}, "
                f"status={prediction_result['status']}, "
                f"inference_time_ms={prediction_result['inference_time_ms']}"
            )
            
            # Step 2: Create inspection record data
            inspection_data = InspectionCreate(
                product_id=product_id,
                image_path=image_path,
                heatmap_path=prediction_result['heatmap_path'],
                anomaly_score=prediction_result['anomaly_score'],
                status=prediction_result['status'],
                inference_time_ms=prediction_result['inference_time_ms']
            )
            
            # Step 3: Persist inspection record to database
            # The repository handles its own transaction management (commit/rollback)
            created_record = self.repository.create(inspection_data)
            
            logger.info(
                f"Inspection workflow completed successfully: "
                f"inspection_id={created_record.id}, "
                f"product_id={product_id}, "
                f"status={created_record.status}"
            )
            
            return created_record
            
        except InferenceError as e:
            # Handle inference-specific errors
            error_msg = f"Inference failed during inspection workflow: {str(e)}"
            logger.error(error_msg)
            
            # Database rollback is handled by repository if record creation failed
            # No cleanup needed for inference failures before DB operation
            
            raise InspectionServiceError(error_msg) from e
            
        except SQLAlchemyError as e:
            # Handle database errors
            error_msg = f"Database error during inspection workflow: {str(e)}"
            logger.error(error_msg)
            
            # Database rollback is handled by repository
            # The inference has already run, but the record wasn't saved
            # This is acceptable - the heatmap file remains but orphaned
            # Could implement cleanup logic here if needed
            
            raise InspectionServiceError(error_msg) from e
            
        except Exception as e:
            # Handle unexpected errors
            error_msg = f"Unexpected error during inspection workflow: {str(e)}"
            logger.error(error_msg)
            
            # If we've created a record, try to roll back
            if created_record:
                try:
                    self.db.rollback()
                except Exception as rollback_error:
                    logger.error(f"Error during rollback: {rollback_error}")
            
            raise InspectionServiceError(error_msg) from e
    
    def get_inspection_by_id(self, inspection_id: int) -> Optional[Inspection]:
        """
        Retrieve a single inspection record by ID.
        
        This is a convenience method that delegates to the repository.
        Provided for completeness and to give the service layer a unified
        interface for API endpoints.
        
        Args:
            inspection_id: Unique identifier of the inspection record
            
        Returns:
            Optional[Inspection]: Inspection record if found, None otherwise
            
        Raises:
            InspectionServiceError: If database query fails
        
        Example:
            >>> inspection = service.get_inspection_by_id(42)
            >>> if inspection:
            ...     print(f"Found: {inspection.product_id}")
            Found: PROD-123
        """
        try:
            return self.repository.get_by_id(inspection_id)
        except SQLAlchemyError as e:
            error_msg = f"Error retrieving inspection by id={inspection_id}: {str(e)}"
            logger.error(error_msg)
            raise InspectionServiceError(error_msg) from e
    
    def get_all_inspections(self) -> list[Inspection]:
        """
        Retrieve all inspection records ordered by created_at descending.
        
        This is a convenience method that delegates to the repository.
        Provided for completeness and to give the service layer a unified
        interface for API endpoints.
        
        Returns:
            list[Inspection]: List of inspection records ordered by created_at DESC
                             (empty list if no records exist)
            
        Raises:
            InspectionServiceError: If database query fails
        
        Example:
            >>> inspections = service.get_all_inspections()
            >>> for inspection in inspections:
            ...     print(f"{inspection.id}: {inspection.status}")
            3: PASS
            2: REJECT
            1: REVIEW
        """
        try:
            return self.repository.get_all()
        except SQLAlchemyError as e:
            error_msg = f"Error retrieving all inspections: {str(e)}"
            logger.error(error_msg)
            raise InspectionServiceError(error_msg) from e
