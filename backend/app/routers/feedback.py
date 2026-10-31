"""
Feedback API Endpoints

REST API endpoints for inspector feedback operations.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app.services.feedback import FeedbackService, FeedbackServiceError
from app.schemas.feedback import FeedbackCreate, FeedbackResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/feedback",
    tags=["feedback"]
)


@router.post("", response_model=FeedbackResponse, status_code=201)
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    Submit inspector feedback for an inspection.
    
    Args:
        feedback_data: Feedback creation request
        db: Database session
        
    Returns:
        Created feedback record
        
    Raises:
        HTTPException: If validation or creation fails
    """
    try:
        service = FeedbackService(db)
        feedback = service.create_feedback(feedback_data)
        
        return FeedbackResponse(
            id=feedback.id,
            inspection_id=feedback.inspection_id,
            feedback_type=feedback.feedback_type,
            comments=feedback.comments,
            created_at=feedback.created_at
        )
        
    except FeedbackServiceError as e:
        logger.error(f"Feedback service error: {str(e)}")
        # Check if it's a not found error
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error creating feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=List[FeedbackResponse], status_code=200)
async def list_feedback(db: Session = Depends(get_db)):
    """
    Retrieve all feedback records.
    
    Args:
        db: Database session
        
    Returns:
        List of feedback records
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        service = FeedbackService(db)
        feedback_list = service.get_all_feedback()
        
        return [
            FeedbackResponse(
                id=feedback.id,
                inspection_id=feedback.inspection_id,
                feedback_type=feedback.feedback_type,
                comments=feedback.comments,
                created_at=feedback.created_at
            )
            for feedback in feedback_list
        ]
        
    except FeedbackServiceError as e:
        logger.error(f"Feedback service error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error retrieving feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
