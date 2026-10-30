"""
Middleware Package

Contains middleware and error handlers for the INSPECTRA backend.
"""

from app.middleware.error_handlers import register_error_handlers

__all__ = ["register_error_handlers"]
