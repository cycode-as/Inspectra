"""
Feedback Repository

Data access layer for feedback operations.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate


class FeedbackRepository:
    """
    Repository for feedback database operations.
    
    Provides CRUD operations for feedback records.
    """
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def create(self, feedback_data: FeedbackCreate) -> Feedback:
        """
        Create a new feedback record.
        
        Args:
            feedback_data: Feedback creation schema
            
        Returns:
            Created feedback record
        """
        feedback = Feedback(
            inspection_id=feedback_data.inspection_id,
            feedback_type=feedback_data.feedback_type,
            comments=feedback_data.comments
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback
    
    def get_all(self) -> List[Feedback]:
        """
        Retrieve all feedback records ordered by created_at descending.
        
        Returns:
            List of feedback records
        """
        return self.db.query(Feedback).order_by(Feedback.created_at.desc()).all()
    
    def get_by_inspection_id(self, inspection_id: int) -> List[Feedback]:
        """
        Retrieve feedback for a specific inspection.
        
        Args:
            inspection_id: Inspection ID
            
        Returns:
            List of feedback records for the inspection
        """
        return self.db.query(Feedback).filter(
            Feedback.inspection_id == inspection_id
        ).order_by(Feedback.created_at.desc()).all()
