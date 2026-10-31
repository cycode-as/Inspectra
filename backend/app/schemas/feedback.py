"""
Feedback Schema Models

Pydantic models for request/response validation in feedback endpoints.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal, Optional


class FeedbackCreate(BaseModel):
    """
    Schema for creating feedback.
    
    Attributes:
        inspection_id: ID of the inspection being reviewed
        feedback_type: Classification of feedback
        comments: Optional detailed comments
    """
    inspection_id: int = Field(..., gt=0)
    feedback_type: Literal[
        "Correct prediction",
        "False positive",
        "Missed defect",
        "Needs manual review"
    ]
    comments: Optional[str] = Field(None, max_length=2000)
    
    @field_validator('feedback_type')
    @classmethod
    def validate_feedback_type(cls, v: str) -> str:
        """Validate feedback_type is one of allowed values."""
        allowed_types = {
            "Correct prediction",
            "False positive",
            "Missed defect",
            "Needs manual review"
        }
        if v not in allowed_types:
            raise ValueError(f"feedback_type must be one of {allowed_types}, got '{v}'")
        return v


class FeedbackResponse(BaseModel):
    """
    Schema for feedback API responses.
    
    Attributes:
        id: Unique feedback identifier
        inspection_id: Referenced inspection ID
        feedback_type: Classification of feedback
        comments: Optional detailed comments
        created_at: Timestamp of feedback submission
    """
    id: int
    inspection_id: int
    feedback_type: str
    comments: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
