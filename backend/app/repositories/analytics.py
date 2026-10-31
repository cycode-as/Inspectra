"""
Analytics Repository

Data access layer for analytics queries.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from typing import Dict, List, Tuple
from datetime import date
from app.models.inspection import Inspection


class AnalyticsRepository:
    """
    Repository for analytics database queries.
    
    Provides aggregation queries for reporting and statistics.
    """
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def get_summary_stats(self) -> Dict[str, int]:
        """
        Get overall inspection summary statistics.
        
        Returns:
            Dictionary with total, pass, review, and reject counts
        """
        total = self.db.query(func.count(Inspection.id)).scalar() or 0
        pass_count = self.db.query(func.count(Inspection.id)).filter(
            Inspection.status == "PASS"
        ).scalar() or 0
        review_count = self.db.query(func.count(Inspection.id)).filter(
            Inspection.status == "REVIEW"
        ).scalar() or 0
        reject_count = self.db.query(func.count(Inspection.id)).filter(
            Inspection.status == "REJECT"
        ).scalar() or 0
        
        return {
            "total": total,
            "pass_count": pass_count,
            "review_count": review_count,
            "reject_count": reject_count
        }
    
    def get_daily_trends(self) -> List[Tuple[date, int, int, int, int]]:
        """
        Get daily inspection trends grouped by date.
        
        Returns:
            List of tuples (date, total, pass_count, review_count, reject_count)
        """
        # Cast datetime to date for grouping
        date_column = cast(Inspection.created_at, Date)
        
        # Aggregate by date
        results = self.db.query(
            date_column.label('inspection_date'),
            func.count(Inspection.id).label('total'),
            func.sum(
                func.cast(
                    (Inspection.status == "PASS"),
                    Integer
                )
            ).label('pass_count'),
            func.sum(
                func.cast(
                    (Inspection.status == "REVIEW"),
                    Integer
                )
            ).label('review_count'),
            func.sum(
                func.cast(
                    (Inspection.status == "REJECT"),
                    Integer
                )
            ).label('reject_count')
        ).group_by(date_column).order_by(date_column.desc()).all()
        
        return [
            (
                row.inspection_date,
                row.total,
                row.pass_count or 0,
                row.review_count or 0,
                row.reject_count or 0
            )
            for row in results
        ]


# Import Integer for type casting
from sqlalchemy import Integer
