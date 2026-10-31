"""
Analytics Schema Models

Pydantic models for analytics and reporting endpoints.
"""

from pydantic import BaseModel, Field
from datetime import date
from typing import List


class AnalyticsSummary(BaseModel):
    """
    Schema for overall analytics summary.
    
    Attributes:
        total_inspections: Total number of inspections
        pass_count: Number of PASS results
        review_count: Number of REVIEW results
        reject_count: Number of REJECT results
        defect_rate: Percentage of rejected products
    """
    total_inspections: int = Field(..., ge=0)
    pass_count: int = Field(..., ge=0)
    review_count: int = Field(..., ge=0)
    reject_count: int = Field(..., ge=0)
    defect_rate: float = Field(..., ge=0.0, le=100.0)


class DailyTrend(BaseModel):
    """
    Schema for daily inspection trends.
    
    Attributes:
        date: Date of inspections
        total: Total inspections on this date
        pass_count: PASS count
        review_count: REVIEW count
        reject_count: REJECT count
    """
    date: date
    total: int = Field(..., ge=0)
    pass_count: int = Field(..., ge=0)
    review_count: int = Field(..., ge=0)
    reject_count: int = Field(..., ge=0)


class AnalyticsTrends(BaseModel):
    """
    Schema for analytics trends response.
    
    Attributes:
        trends: List of daily trend data
    """
    trends: List[DailyTrend]
