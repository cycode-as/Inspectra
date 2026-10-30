"""
Repository Pattern Implementation

This package contains repository classes for database operations.
Repositories abstract database access logic and provide a clean interface
for data persistence operations.
"""

from app.repositories.inspection import InspectionRepository

__all__ = ["InspectionRepository"]
