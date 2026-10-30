"""
Routers Package

This package contains API route definitions for the INSPECTRA backend.
"""

from app.routers.inspections import router as inspections_router

__all__ = ["inspections_router"]
