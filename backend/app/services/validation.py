"""
Image Validation Service Module

Handles validation of uploaded image files, including format checking,
size validation, and unique filename generation.
"""

from fastapi import UploadFile
import os
import uuid
from typing import Set
from config import settings


class ImageValidator:
    """
    Service for validating uploaded image files.
    
    Validates:
    - File extensions (must be PNG, JPG, or JPEG)
    - File size (must not exceed MAX_FILE_SIZE)
    
    Provides:
    - Unique filename generation while preserving extensions
    - File extension extraction utilities
    """
    
    # Allowed image file extensions
    ALLOWED_EXTENSIONS: Set[str] = {"png", "jpg", "jpeg"}
    
    # Maximum file size: 10 MB
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    
    @staticmethod
    def validate_image(file: UploadFile) -> None:
        """
        Validate uploaded image file.
        
        Checks:
        1. File extension is in ALLOWED_EXTENSIONS (case-insensitive)
        2. File size does not exceed MAX_FILE_SIZE
        
        Args:
            file: FastAPI UploadFile object containing the uploaded file
        
        Raises:
            ValueError: If validation fails with a descriptive message
        """
        # Check if filename exists
        if not file.filename:
            raise ValueError("No filename provided")
        
        # Validate file extension
        extension = ImageValidator.get_file_extension(file.filename)
        if extension.lower() not in ImageValidator.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Invalid file format. Allowed formats: {', '.join(ImageValidator.ALLOWED_EXTENSIONS).upper()}"
            )
        
        # Validate file size
        # Read file content to check size
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)  # Reset file pointer to beginning
        
        if file_size > ImageValidator.MAX_FILE_SIZE:
            max_size_mb = ImageValidator.MAX_FILE_SIZE / (1024 * 1024)
            raise ValueError(
                f"File size exceeds maximum allowed size of {max_size_mb:.0f} MB"
            )
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """
        Extract file extension from filename.
        
        Args:
            filename: Name of the file (e.g., "image.jpg")
        
        Returns:
            str: File extension without the dot (e.g., "jpg")
            Returns empty string if no extension found
        """
        if '.' not in filename:
            return ""
        return filename.rsplit('.', 1)[-1]
    
    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """
        Generate unique filename while preserving original file extension.
        
        Uses UUID4 to ensure uniqueness and prevents filename collisions.
        
        Args:
            original_filename: Original name of the uploaded file
        
        Returns:
            str: Unique filename with preserved extension (e.g., "uuid4.jpg")
        """
        extension = ImageValidator.get_file_extension(original_filename)
        unique_id = str(uuid.uuid4())
        
        if extension:
            return f"{unique_id}.{extension}"
        return unique_id
