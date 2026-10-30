"""
Inspection API Endpoints

REST API endpoints for image inspection operations.
Handles image upload, AI inference, and inspection record retrieval.
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging
import os

from app.database import get_db
from app.services.inspection import InspectionService, InspectionServiceError
from app.services.inference import InferenceService, mock_predict_function
from app.services.validation import ImageValidator
from app.services.storage import FileStorageService
from app.schemas.inspection import InspectionResponse, ErrorResponse
from config import get_settings

# Configure logging
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create router
router = APIRouter(
    prefix="/inspections",
    tags=["inspections"]
)


@router.post("/", response_model=InspectionResponse, status_code=200)
async def create_inspection(
    file: UploadFile = File(...),
    product_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload and inspect a product image.
    
    This endpoint:
    1. Validates the uploaded image (format and size)
    2. Saves the image to the uploads directory
    3. Calls AI inference to analyze the image
    4. Stores the inspection record in the database
    5. Returns the complete inspection data
    
    Args:
        file: Uploaded image file (PNG, JPG, or JPEG, max 10MB)
        product_id: Product identifier
        db: Database session (injected)
    
    Returns:
        InspectionResponse: Complete inspection record with URLs
    
    Raises:
        HTTPException 400: If file validation fails
        HTTPException 500: If inference or database operation fails
    """
    try:
        # Step 1: Validate the uploaded image
        ImageValidator.validate_image(file)
        
        # Step 2: Generate unique filename and save the file
        storage_service = FileStorageService()
        unique_filename = ImageValidator.generate_unique_filename(file.filename)
        image_path = storage_service.save_upload(file, unique_filename)
        
        logger.info(f"Image saved: {image_path}")
        
        # Step 3: Initialize services and process inspection
        inference_service = InferenceService(mock_predict_function)
        inspection_service = InspectionService(
            db=db,
            inference_service=inference_service,
            storage_service=storage_service
        )
        
        # Process the inspection workflow
        inspection = inspection_service.process_inspection(
            image_path=image_path,
            product_id=product_id
        )
        
        # Step 4: Build response with image URLs
        image_filename = os.path.basename(inspection.image_path)
        heatmap_filename = os.path.basename(inspection.heatmap_path)
        
        response = InspectionResponse(
            id=inspection.id,
            product_id=inspection.product_id,
            image_url=f"/uploads/{image_filename}",
            heatmap_url=f"/results/{heatmap_filename}",
            anomaly_score=inspection.anomaly_score,
            status=inspection.status,
            inference_time_ms=inspection.inference_time_ms,
            created_at=inspection.created_at
        )
        
        return response
        
    except ValueError as e:
        # Validation errors (from ImageValidator)
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except InspectionServiceError as e:
        # Inspection workflow errors
        logger.error(f"Inspection service error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error during inspection: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=List[InspectionResponse], status_code=200)
async def list_inspections(db: Session = Depends(get_db)):
    """
    Retrieve all inspection records.
    
    Returns all inspections ordered by creation time (most recent first).
    Returns an empty array if no inspections exist.
    
    Args:
        db: Database session (injected)
    
    Returns:
        List[InspectionResponse]: List of inspection records
    
    Raises:
        HTTPException 500: If database query fails
    """
    try:
        # Initialize services
        inference_service = InferenceService(mock_predict_function)
        storage_service = FileStorageService()
        inspection_service = InspectionService(
            db=db,
            inference_service=inference_service,
            storage_service=storage_service
        )
        
        # Retrieve all inspections
        inspections = inspection_service.get_all_inspections()
        
        # Build response list with image URLs
        response_list = []
        for inspection in inspections:
            image_filename = os.path.basename(inspection.image_path)
            heatmap_filename = os.path.basename(inspection.heatmap_path)
            
            response = InspectionResponse(
                id=inspection.id,
                product_id=inspection.product_id,
                image_url=f"/uploads/{image_filename}",
                heatmap_url=f"/results/{heatmap_filename}",
                anomaly_score=inspection.anomaly_score,
                status=inspection.status,
                inference_time_ms=inspection.inference_time_ms,
                created_at=inspection.created_at
            )
            response_list.append(response)
        
        return response_list
        
    except InspectionServiceError as e:
        logger.error(f"Error retrieving inspections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error retrieving inspections: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{inspection_id}", response_model=InspectionResponse, status_code=200)
async def get_inspection(inspection_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single inspection record by ID.
    
    Args:
        inspection_id: Unique inspection identifier
        db: Database session (injected)
    
    Returns:
        InspectionResponse: Inspection record
    
    Raises:
        HTTPException 404: If inspection not found
        HTTPException 400: If inspection_id is invalid
        HTTPException 500: If database query fails
    """
    try:
        # Initialize services
        inference_service = InferenceService(mock_predict_function)
        storage_service = FileStorageService()
        inspection_service = InspectionService(
            db=db,
            inference_service=inference_service,
            storage_service=storage_service
        )
        
        # Retrieve inspection by ID
        inspection = inspection_service.get_inspection_by_id(inspection_id)
        
        if inspection is None:
            raise HTTPException(
                status_code=404,
                detail=f"Inspection with id {inspection_id} not found"
            )
        
        # Build response with image URLs
        image_filename = os.path.basename(inspection.image_path)
        heatmap_filename = os.path.basename(inspection.heatmap_path)
        
        response = InspectionResponse(
            id=inspection.id,
            product_id=inspection.product_id,
            image_url=f"/uploads/{image_filename}",
            heatmap_url=f"/results/{heatmap_filename}",
            anomaly_score=inspection.anomaly_score,
            status=inspection.status,
            inference_time_ms=inspection.inference_time_ms,
            created_at=inspection.created_at
        )
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except InspectionServiceError as e:
        logger.error(f"Error retrieving inspection {inspection_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error retrieving inspection {inspection_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Endpoint for direct POST to /inspect (alternative path)
@router.post("/inspect", response_model=InspectionResponse, status_code=200, include_in_schema=False)
async def create_inspection_alt(
    file: UploadFile = File(...),
    product_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Alternative endpoint path for inspection (delegates to main endpoint)."""
    return await create_inspection(file=file, product_id=product_id, db=db)
