"""
Feedback ORM Model

Defines the SQLAlchemy ORM model for inspector feedback on inspection results.
Supports quality improvement and AI model retraining.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Feedback(Base):
    """
    Feedback database model.
    
    Stores human inspector feedback on AI inspection results for quality tracking
    and future model improvement.
    
    Attributes:
        id (int): Primary key, auto-incrementing feedback identifier
        inspection_id (int): Foreign key referencing inspections.id
        feedback_type (str): Type of feedback (Correct prediction, False positive, etc.)
        comments (str): Optional detailed comments from inspector
        created_at (datetime): Timestamp of feedback submission
    """
    
    __tablename__ = "feedback"
    
    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Unique feedback identifier"
    )
    
    # Foreign key to inspections table
    inspection_id = Column(
        Integer,
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to inspection record"
    )
    
    # Feedback classification
    feedback_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Type of feedback: Correct prediction, False positive, Missed defect, Needs manual review"
    )
    
    # Optional detailed comments
    comments = Column(
        Text,
        nullable=True,
        comment="Optional detailed feedback comments"
    )
    
    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Timestamp of feedback submission"
    )
    
    # Relationship to inspection (optional, for easier querying)
    # inspection = relationship("Inspection", backref="feedbacks")
    
    # Indexes for query optimization
    __table_args__ = (
        Index('idx_feedback_type_created', 'feedback_type', 'created_at'),
    )
    
    def __repr__(self) -> str:
        """String representation of Feedback instance."""
        return (
            f"<Feedback(id={self.id}, "
            f"inspection_id={self.inspection_id}, "
            f"feedback_type='{self.feedback_type}', "
            f"created_at={self.created_at})>"
        )
