"""
QR Code Generation Service

Service for generating QR codes for inspection deep links.
"""

import qrcode
from PIL import Image
import os
from typing import Optional


class QRCodeService:
    """
    Service for generating QR codes linking to inspection details.
    
    Creates high-resolution QR codes for digital defect passports.
    """
    
    def __init__(self, output_dir: str = "uploads/qrs", base_url: str = "http://localhost:3000"):
        """
        Initialize QR code service.
        
        Args:
            output_dir: Directory to store generated QR codes
            base_url: Base URL for frontend application
        """
        self.output_dir = output_dir
        self.base_url = base_url
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_qr_code(self, inspection_id: int) -> str:
        """
        Generate a QR code for an inspection.
        
        Args:
            inspection_id: Inspection ID
            
        Returns:
            Path to generated QR code image
        """
        # Create deep link URL
        inspection_url = f"{self.base_url}/inspections/{inspection_id}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,  # Auto-adjust version based on data
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
            box_size=10,  # Size of each box in pixels
            border=4,  # Border size in boxes
        )
        qr.add_data(inspection_url)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to file
        filename = f"inspection_qr_{inspection_id}.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath)
        
        return filepath
    
    def get_qr_url(self, inspection_id: int) -> str:
        """
        Get the URL path for a QR code.
        
        Args:
            inspection_id: Inspection ID
            
        Returns:
            URL path to QR code
        """
        filename = f"inspection_qr_{inspection_id}.png"
        return f"/uploads/qrs/{filename}"
