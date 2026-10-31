"""
Analytics API Endpoints

REST API endpoints for analytics and reporting.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.services.analytics import AnalyticsService
from app.schemas.analytics import AnalyticsSummary, AnalyticsTrends

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/analytics",
    tags=["analytics"]
)


@router.get("/summary", response_model=AnalyticsSummary, status_code=200)
async def get_analytics_summary(db: Session = Depends(get_db)):
    """
    Get overall analytics summary.
    
    Returns total inspections, status counts, and defect rate.
    
    Args:
        db: Database session
        
    Returns:
        Analytics summary
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        service = AnalyticsService(db)
        summary = service.get_summary()
        return summary
        
    except Exception as e:
        logger.error(f"Error retrieving analytics summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/trends", response_model=AnalyticsTrends, status_code=200)
async def get_analytics_trends(db: Session = Depends(get_db)):
    """
    Get daily inspection trends.
    
    Returns daily inspection counts grouped by date and status.
    
    Args:
        db: Database session
        
    Returns:
        Analytics trends
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        service = AnalyticsService(db)
        trends = service.get_trends()
        return trends
        
    except Exception as e:
        logger.error(f"Error retrieving analytics trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
