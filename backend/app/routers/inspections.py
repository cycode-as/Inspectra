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
import sys

# Add the root 'inspectra' directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))) 

# Import Member 1's real predict function
from ai_module.predict import predict

from app.database import get_db
from app.services.inspection import InspectionService, InspectionServiceError
from app.services.inference import InferenceService  # <-- DO NOT import predict from here
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
    tags=["inspections"]
)


@router.post("/inspect", response_model=InspectionResponse, status_code=200)
async def create_inspection(
    file: UploadFile = File(...),
    product_id: str = Form("AUTO-GEN-ID"),
    db: Session = Depends(get_db)
):
    try:
        # Step 1: Validate the uploaded image
        ImageValidator.validate_image(file)
        
        # Step 2: Generate unique filename and save the file
        storage_service = FileStorageService()
        unique_filename = ImageValidator.generate_unique_filename(file.filename)
        image_path = storage_service.save_upload(file, unique_filename)
        
        logger.info(f"Image saved: {image_path}")
        
        # Step 3: Initialize services with the REAL predict function
        inference_service = InferenceService(predict)
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
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except InspectionServiceError as e:
        logger.error(f"Inspection service error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error during inspection: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/inspections", response_model=List[InspectionResponse], status_code=200)
async def list_inspections(db: Session = Depends(get_db)):
    try:
        inference_service = InferenceService(predict)
        storage_service = FileStorageService()
        inspection_service = InspectionService(
            db=db,
            inference_service=inference_service,
            storage_service=storage_service
        )
        
        inspections = inspection_service.get_all_inspections()
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
        
    except Exception as e:
        logger.error(f"Unexpected error retrieving inspections: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/inspections/{inspection_id}", response_model=InspectionResponse, status_code=200)
async def get_inspection(inspection_id: int, db: Session = Depends(get_db)):
    try:
        inference_service = InferenceService(predict)
        storage_service = FileStorageService()
        inspection_service = InspectionService(
            db=db,
            inference_service=inference_service,
            storage_service=storage_service
        )
        
        inspection = inspection_service.get_inspection_by_id(inspection_id)
        if inspection is None:
            raise HTTPException(status_code=404, detail=f"Inspection with id {inspection_id} not found")
        
        image_filename = os.path.basename(inspection.image_path)
        heatmap_filename = os.path.basename(inspection.heatmap_path)
        
        return InspectionResponse(
            id=inspection.id,
            product_id=inspection.product_id,
            image_url=f"/uploads/{image_filename}",
            heatmap_url=f"/results/{heatmap_filename}",
            anomaly_score=inspection.anomaly_score,
            status=inspection.status,
            inference_time_ms=inspection.inference_time_ms,
            created_at=inspection.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving inspection {inspection_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")