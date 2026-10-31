"""
Feedback Service

Business logic for feedback operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import logging
from app.repositories.feedback import FeedbackRepository
from app.repositories.inspection import InspectionRepository
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.models.feedback import Feedback


logger = logging.getLogger(__name__)


class FeedbackServiceError(Exception):
    """Exception raised when feedback service operations fail."""
    pass


class FeedbackService:
    """
    Service for managing inspector feedback.
    
    Handles feedback creation and retrieval with validation.
    """
    
    def __init__(self, db: Session):
        """Initialize feedback service."""
        self.db = db
        self.repository = FeedbackRepository(db)
        self.inspection_repository = InspectionRepository(db)
    
    def create_feedback(self, feedback_data: FeedbackCreate) -> Feedback:
        """
        Create new feedback record.
        
        Args:
            feedback_data: Feedback creation schema
            
        Returns:
            Created feedback record
            
        Raises:
            FeedbackServiceError: If validation or creation fails
        """
        try:
            # Validate that inspection exists
            inspection = self.inspection_repository.get_by_id(feedback_data.inspection_id)
            if not inspection:
                raise FeedbackServiceError(
                    f"Inspection with id {feedback_data.inspection_id} not found"
                )
            
            # Create feedback
            feedback = self.repository.create(feedback_data)
            logger.info(f"Feedback created: id={feedback.id}, inspection_id={feedback_data.inspection_id}")
            
            return feedback
            
        except FeedbackServiceError:
            raise
        except SQLAlchemyError as e:
            error_msg = f"Database error creating feedback: {str(e)}"
            logger.error(error_msg)
            raise FeedbackServiceError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error creating feedback: {str(e)}"
            logger.error(error_msg)
            raise FeedbackServiceError(error_msg) from e
    
    def get_all_feedback(self) -> List[Feedback]:
        """
        Retrieve all feedback records.
        
        Returns:
            List of feedback records
            
        Raises:
            FeedbackServiceError: If retrieval fails
        """
        try:
            return self.repository.get_all()
        except SQLAlchemyError as e:
            error_msg = f"Database error retrieving feedback: {str(e)}"
            logger.error(error_msg)
            raise FeedbackServiceError(error_msg) from e
