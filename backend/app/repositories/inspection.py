"""
Inspection Repository

Repository pattern implementation for inspection database operations.
Provides clean interface for creating and retrieving inspection records.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.models.inspection import Inspection
from app.schemas.inspection import InspectionCreate

# Configure logging
logger = logging.getLogger(__name__)


class InspectionRepository:
    """
    Repository for inspection database operations.
    
    Handles all database operations for inspection records following
    the repository pattern. Provides methods for creating and retrieving
    inspection records with proper error handling and logging.
    
    Attributes:
        db (Session): SQLAlchemy database session
    """
    
    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create(self, inspection_data: InspectionCreate) -> Inspection:
        """
        Create a new inspection record in the database.
        
        Takes inspection data validated by Pydantic schema, creates a new
        Inspection ORM model, persists it to the database, and returns the
        created record with auto-generated id and created_at timestamp.
        
        Args:
            inspection_data: Validated inspection data (InspectionCreate schema)
            
        Returns:
            Inspection: Created inspection record with id and created_at populated
            
        Raises:
            SQLAlchemyError: If database operation fails
            
        Example:
            >>> inspection_data = InspectionCreate(
            ...     product_id="PROD-123",
            ...     image_path="uploads/image.jpg",
            ...     heatmap_path="results/heatmap.jpg",
            ...     anomaly_score=0.75,
            ...     status="REVIEW",
            ...     inference_time_ms=150
            ... )
            >>> inspection = repository.create(inspection_data)
            >>> print(inspection.id)  # Auto-generated ID
            1
        """
        try:
            # Create Inspection ORM model from Pydantic schema
            db_inspection = Inspection(
                product_id=inspection_data.product_id,
                image_path=inspection_data.image_path,
                heatmap_path=inspection_data.heatmap_path,
                anomaly_score=inspection_data.anomaly_score,
                status=inspection_data.status,
                inference_time_ms=inspection_data.inference_time_ms
            )
            
            # Add to session and commit
            self.db.add(db_inspection)
            self.db.commit()
            self.db.refresh(db_inspection)
            
            logger.info(
                f"Created inspection record: id={db_inspection.id}, "
                f"product_id={db_inspection.product_id}, "
                f"status={db_inspection.status}"
            )
            
            return db_inspection
            
        except SQLAlchemyError as e:
            # Rollback transaction on error
            self.db.rollback()
            logger.error(f"Error creating inspection record: {e}")
            raise
    
    def get_all(self) -> List[Inspection]:
        """
        Retrieve all inspection records ordered by created_at descending.
        
        Returns all inspection records from the database sorted by creation
        timestamp in descending order (most recent first). Returns an empty
        list if no records exist.
        
        Returns:
            List[Inspection]: List of inspection records ordered by created_at DESC
                             (empty list if no records exist)
            
        Raises:
            SQLAlchemyError: If database query fails
            
        Example:
            >>> inspections = repository.get_all()
            >>> for inspection in inspections:
            ...     print(f"{inspection.id}: {inspection.created_at}")
            3: 2024-01-15 14:30:00
            2: 2024-01-15 10:15:00
            1: 2024-01-15 09:00:00
        """
        try:
            inspections = (
                self.db.query(Inspection)
                .order_by(Inspection.created_at.desc())
                .all()
            )
            
            logger.info(f"Retrieved {len(inspections)} inspection records")
            
            return inspections
            
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving inspection records: {e}")
            raise
    
    def get_by_id(self, inspection_id: int) -> Optional[Inspection]:
        """
        Retrieve a single inspection record by ID.
        
        Queries the database for an inspection record with the specified ID.
        Returns the inspection record if found, or None if no record exists
        with the given ID.
        
        Args:
            inspection_id: Unique identifier of the inspection record
            
        Returns:
            Optional[Inspection]: Inspection record if found, None otherwise
            
        Raises:
            SQLAlchemyError: If database query fails
            
        Example:
            >>> inspection = repository.get_by_id(42)
            >>> if inspection:
            ...     print(f"Found: {inspection.product_id}")
            ... else:
            ...     print("Inspection not found")
            Found: PROD-123
        """
        try:
            inspection = (
                self.db.query(Inspection)
                .filter(Inspection.id == inspection_id)
                .first()
            )
            
            if inspection:
                logger.info(f"Retrieved inspection record: id={inspection_id}")
            else:
                logger.info(f"Inspection record not found: id={inspection_id}")
            
            return inspection
            
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving inspection by id={inspection_id}: {e}")
            raise
