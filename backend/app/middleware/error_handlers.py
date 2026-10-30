"""
Global Error Handlers

Centralized exception handlers for consistent error responses across the API.
Ensures all errors return JSON in the format: {"error": "...", "detail": "..."}
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.services.inference import InferenceError
from app.services.inspection import InspectionServiceError

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """
    Register all error handlers with the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handle Pydantic validation errors (400 Bad Request).
        
        Triggered when request data doesn't match expected schema.
        """
        error_details = []
        for error in exc.errors():
            loc = " -> ".join(str(x) for x in error["loc"])
            error_details.append(f"{loc}: {error['msg']}")
        
        detail = "; ".join(error_details)
        
        logger.warning(f"Validation error: {detail}")
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Validation failed",
                "detail": detail
            }
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """
        Handle ValueError exceptions (400 Bad Request).
        
        Triggered by image validation failures and other input errors.
        """
        logger.warning(f"Value error: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Invalid input",
                "detail": str(exc)
            }
        )
    
    @app.exception_handler(InferenceError)
    async def inference_error_handler(request: Request, exc: InferenceError):
        """
        Handle AI inference errors (500 Internal Server Error).
        
        Triggered when AI prediction function fails.
        """
        logger.error(f"Inference error: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Inference failed",
                "detail": str(exc)
            }
        )
    
    @app.exception_handler(InspectionServiceError)
    async def inspection_service_error_handler(request: Request, exc: InspectionServiceError):
        """
        Handle inspection service errors (500 Internal Server Error).
        
        Triggered when inspection workflow fails.
        """
        logger.error(f"Inspection service error: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Inspection service failed",
                "detail": str(exc)
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def database_error_handler(request: Request, exc: SQLAlchemyError):
        """
        Handle database errors (500 Internal Server Error).
        
        Triggered when database operations fail.
        """
        logger.error(f"Database error: {str(exc)}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Database operation failed",
                "detail": "An error occurred while accessing the database"
            }
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """
        Handle all other unexpected exceptions (500 Internal Server Error).
        
        Catch-all handler for any unhandled exceptions.
        """
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred"
            }
        )
    
    logger.info("Error handlers registered successfully")
