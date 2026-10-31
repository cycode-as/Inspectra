"""
Reports API Endpoints

REST API endpoints for PDF reports and QR code generation.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import logging
import os

from app.database import get_db
from app.services.inspection import InspectionService
from app.services.inference import InferenceService
from app.services.pdf_report import PDFReportService
from app.services.qr_code import QRCodeService
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(
    prefix="/api/inspections",
    tags=["reports"]
)


@router.get("/{inspection_id}/report", response_class=FileResponse)
async def generate_inspection_report(
    inspection_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate and download PDF inspection report.
    
    Args:
        inspection_id: Inspection ID
        db: Database session
        
    Returns:
        PDF file response
        
    Raises:
        HTTPException: If inspection not found or generation fails
    """
    try:
        # Import predict function for service initialization
        import sys
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
        from ai_module.predict import predict
        
        # Get inspection record
        inference_service = InferenceService(predict)
        inspection_service = InspectionService(db, inference_service)
        inspection = inspection_service.get_inspection_by_id(inspection_id)
        
        if not inspection:
            raise HTTPException(status_code=404, detail=f"Inspection {inspection_id} not found")
        
        # Generate PDF report
        pdf_service = PDFReportService()
        report_path = pdf_service.generate_report(inspection)
        
        logger.info(f"Generated PDF report: {report_path}")
        
        # Return as downloadable file
        return FileResponse(
            path=report_path,
            media_type="application/pdf",
            filename=f"inspection_report_{inspection_id}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report for inspection {inspection_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{inspection_id}/qr", response_class=FileResponse)
async def generate_inspection_qr(
    inspection_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate and download QR code for inspection.
    
    Args:
        inspection_id: Inspection ID
        db: Database session
        
    Returns:
        QR code image file response
        
    Raises:
        HTTPException: If inspection not found or generation fails
    """
    try:
        # Import predict function for service initialization
        import sys
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
        from ai_module.predict import predict
        
        # Verify inspection exists
        inference_service = InferenceService(predict)
        inspection_service = InspectionService(db, inference_service)
        inspection = inspection_service.get_inspection_by_id(inspection_id)
        
        if not inspection:
            raise HTTPException(status_code=404, detail=f"Inspection {inspection_id} not found")
        
        # Generate QR code
        qr_service = QRCodeService()
        qr_path = qr_service.generate_qr_code(inspection_id)
        
        logger.info(f"Generated QR code: {qr_path}")
        
        # Return as downloadable file
        return FileResponse(
            path=qr_path,
            media_type="image/png",
            filename=f"inspection_qr_{inspection_id}.png"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating QR code for inspection {inspection_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
