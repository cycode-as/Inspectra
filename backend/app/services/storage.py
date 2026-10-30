"""
File Storage Service Module

Handles file system operations for uploaded images and result heatmaps.
Manages directory creation, file saving, and URL generation.
"""

from fastapi import UploadFile
import os
import shutil
from pathlib import Path
from config import settings


class FileStorageService:
    """
    Service for managing file storage operations.
    
    Handles:
    - Creation of uploads and results directories
    - Saving uploaded files with unique filenames
    - URL generation for accessing stored files
    """
    
    def __init__(self):
        """Initialize the file storage service and ensure directories exist."""
        self.uploads_dir = settings.uploads_dir
        self.results_dir = settings.results_dir
        self.ensure_directories()
    
    def ensure_directories(self) -> None:
        """
        Create uploads and results directories if they don't exist.
        
        Creates:
        - uploads/ directory for storing uploaded images
        - results/ directory for storing generated heatmaps
        """
        Path(self.uploads_dir).mkdir(parents=True, exist_ok=True)
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
    
    def save_upload(self, file: UploadFile, filename: str) -> str:
        """
        Save uploaded file to uploads directory.
        
        Args:
            file: FastAPI UploadFile object containing the uploaded file
            filename: Unique filename to save the file as (should include extension)
        
        Returns:
            str: Relative path to the saved file (e.g., "uploads/filename.jpg")
        
        Raises:
            IOError: If the save operation fails
        """
        try:
            file_path = os.path.join(self.uploads_dir, filename)
            
            # Save the file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Return relative path
            return file_path
        except Exception as e:
            raise IOError(f"Failed to save uploaded file: {str(e)}")
    
    def get_upload_url(self, filename: str) -> str:
        """
        Generate URL for accessing an uploaded file.
        
        Args:
            filename: Name of the uploaded file
        
        Returns:
            str: URL path for accessing the file (e.g., "/uploads/filename.jpg")
        """
        return f"/{self.uploads_dir}/{filename}"
    
    def get_result_url(self, filename: str) -> str:
        """
        Generate URL for accessing a result heatmap file.
        
        Args:
            filename: Name of the result file
        
        Returns:
            str: URL path for accessing the file (e.g., "/results/filename.jpg")
        """
        return f"/{self.results_dir}/{filename}"
