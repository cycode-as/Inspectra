"""
INSPECTRA FastAPI Backend - Main Application Module

This module initializes the FastAPI application and configures routes,
middleware, and static file serving for the AI-powered defect detection system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
from app.database import init_db, check_db_connection
from app.routers import inspections_router
from app.routers import feedback as feedback_router
from app.routers import analytics as analytics_router
from app.routers import reports as reports_router
from app.middleware import register_error_handlers
from config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Initialize FastAPI application
app = FastAPI(
    title="INSPECTRA API",
    description="AI-powered defect detection backend for product images",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Register global error handlers
register_error_handlers(app)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Application startup handler.
    Initializes directories, database connection, and static file serving.
    """
    logger.info("Starting INSPECTRA backend...")
    
    # Ensure all required directories exist
    directories = [
        settings.uploads_dir,
        settings.results_dir,
        "uploads/reports",  # For PDF reports
        "uploads/qrs"       # For QR codes
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    logger.info(f"Directories ensured: {', '.join(directories)}")
    
    # Check database connection
    logger.info("Checking database connection...")
    if not check_db_connection():
        logger.error("Failed to connect to database!")
        raise Exception("Database connection failed")
    
    # Initialize database tables
    logger.info("Initializing database tables...")
    init_db()
    
    logger.info("INSPECTRA backend started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown handler.
    Performs cleanup operations.
    """
    logger.info("Shutting down INSPECTRA backend...")


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify service status.
    
    Returns:
        dict: Service health status
    """
    return {"status": "healthy", "service": "inspectra-api"}


# Include routers
app.include_router(inspections_router)
app.include_router(feedback_router.router)
app.include_router(analytics_router.router)
app.include_router(reports_router.router)

# Also add /inspect endpoint at root level for convenience
app.include_router(inspections_router, prefix="", tags=["inspect"])

# Mount static file directories
# This allows images to be accessed via /uploads/filename and /results/filename
app.mount("/uploads", StaticFiles(directory=settings.uploads_dir), name="uploads")
app.mount("/results", StaticFiles(directory=settings.results_dir), name="results")

logger.info(f"Static files mounted: /uploads -> {settings.uploads_dir}, /results -> {settings.results_dir}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
