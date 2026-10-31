"""
Routers Package

This package contains API route definitions for the INSPECTRA backend.
"""

from app.routers.inspections import router as inspections_router
from app.routers import feedback
from app.routers import analytics
from app.routers import reports

__all__ = ["inspections_router", "feedback", "analytics", "reports"]
