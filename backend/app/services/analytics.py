"""
Analytics Service

Business logic for analytics and reporting.
"""

from sqlalchemy.orm import Session
from typing import Dict, List
from app.repositories.analytics import AnalyticsRepository
from app.schemas.analytics import AnalyticsSummary, AnalyticsTrends, DailyTrend


class AnalyticsService:
    """
    Service for analytics calculations and reporting.
    
    Provides summary statistics and trend analysis.
    """
    
    def __init__(self, db: Session):
        """Initialize analytics service."""
        self.db = db
        self.repository = AnalyticsRepository(db)
    
    def get_summary(self) -> AnalyticsSummary:
        """
        Get overall analytics summary.
        
        Returns:
            Analytics summary with totals and defect rate
        """
        stats = self.repository.get_summary_stats()
        
        # Calculate defect rate
        total = stats["total"]
        reject_count = stats["reject_count"]
        defect_rate = (reject_count / total * 100) if total > 0 else 0.0
        
        return AnalyticsSummary(
            total_inspections=stats["total"],
            pass_count=stats["pass_count"],
            review_count=stats["review_count"],
            reject_count=stats["reject_count"],
            defect_rate=round(defect_rate, 2)
        )
    
    def get_trends(self) -> AnalyticsTrends:
        """
        Get daily inspection trends.
        
        Returns:
            Analytics trends with daily breakdowns
        """
        trends_data = self.repository.get_daily_trends()
        
        trends = [
            DailyTrend(
                date=trend_date,
                total=total,
                pass_count=pass_count,
                review_count=review_count,
                reject_count=reject_count
            )
            for trend_date, total, pass_count, review_count, reject_count in trends_data
        ]
        
        return AnalyticsTrends(trends=trends)
