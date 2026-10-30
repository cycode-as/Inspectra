"""
Pydantic Schemas Module

Contains request and response validation models for API endpoints.
"""

from .inspection import (
    InspectionCreate,
    InspectionResponse,
    PredictionResult,
    ErrorResponse
)

__all__ = [
    "InspectionCreate",
    "InspectionResponse",
    "PredictionResult",
    "ErrorResponse"
]
