"""
Unit tests for FileStorageService.

Tests file storage operations including:
- Directory creation
- File saving
- URL generation
"""

import pytest
import os
import shutil
from pathlib import Path
from io import BytesIO
from fastapi import UploadFile
from app.services.storage import FileStorageService
from config import settings


@pytest.fixture
def temp_storage_dirs(tmp_path):
    """Create temporary storage directories for testing."""
    uploads_dir = tmp_path / "uploads"
    results_dir = tmp_path / "results"
    
    # Temporarily override settings
    original_uploads = settings.uploads_dir
    original_results = settings.results_dir
    
    settings.uploads_dir = str(uploads_dir)
    settings.results_dir = str(results_dir)
    
    yield uploads_dir, results_dir
    
    # Restore original settings
    settings.uploads_dir = original_uploads
    settings.results_dir = original_results
    
    # Cleanup
    if uploads_dir.exists():
        shutil.rmtree(uploads_dir)
    if results_dir.exists():
        shutil.rmtree(results_dir)


@pytest.fixture
def storage_service(temp_storage_dirs):
    """Create a FileStorageService instance with temporary directories."""
    return FileStorageService()


@pytest.fixture
def mock_upload_file():
    """Create a mock UploadFile for testing."""
    def _create_file(filename: str, content: bytes = b"test image content"):
        file_obj = BytesIO(content)
        return UploadFile(filename=filename, file=file_obj)
    return _create_file


class TestFileStorageService:
    """Test suite for FileStorageService."""
    
    def test_ensure_directories_creates_uploads_dir(self, temp_storage_dirs, storage_service):
        """Test that ensure_directories creates the uploads directory."""
        uploads_dir, _ = temp_storage_dirs
        assert uploads_dir.exists()
        assert uploads_dir.is_dir()
    
    def test_ensure_directories_creates_results_dir(self, temp_storage_dirs, storage_service):
        """Test that ensure_directories creates the results directory."""
        _, results_dir = temp_storage_dirs
        assert results_dir.exists()
        assert results_dir.is_dir()
    
    def test_ensure_directories_idempotent(self, temp_storage_dirs, storage_service):
        """Test that ensure_directories can be called multiple times safely."""
        # Call ensure_directories again
        storage_service.ensure_directories()
        
        uploads_dir, results_dir = temp_storage_dirs
        assert uploads_dir.exists()
        assert results_dir.exists()
    
    def test_save_upload_saves_file(self, storage_service, mock_upload_file, temp_storage_dirs):
        """Test that save_upload saves the file to the uploads directory."""
        uploads_dir, _ = temp_storage_dirs
        filename = "test_image.jpg"
        content = b"test image data"
        
        upload_file = mock_upload_file(filename, content)
        
        result_path = storage_service.save_upload(upload_file, filename)
        
        # Verify file was saved
        expected_path = uploads_dir / filename
        assert expected_path.exists()
        
        # Verify content
        with open(expected_path, "rb") as f:
            saved_content = f.read()
        assert saved_content == content
        
        # Verify return path
        assert result_path == str(uploads_dir / filename)
    
    def test_save_upload_with_unique_filename(self, storage_service, mock_upload_file, temp_storage_dirs):
        """Test that save_upload works with unique filenames."""
        uploads_dir, _ = temp_storage_dirs
        original_filename = "image.jpg"
        unique_filename = "12345678-image.jpg"
        
        upload_file = mock_upload_file(original_filename)
        
        result_path = storage_service.save_upload(upload_file, unique_filename)
        
        # Verify file was saved with unique name
        expected_path = uploads_dir / unique_filename
        assert expected_path.exists()
    
    def test_save_upload_raises_ioerror_on_failure(self, storage_service, mock_upload_file, temp_storage_dirs):
        """Test that save_upload raises IOError when save operation fails."""
        uploads_dir, _ = temp_storage_dirs
        
        # Use invalid path with subdirectory that doesn't exist to cause failure
        invalid_filename = "nonexistent_dir/test.jpg"
        
        upload_file = mock_upload_file("test.jpg")
        
        with pytest.raises(IOError, match="Failed to save uploaded file"):
            storage_service.save_upload(upload_file, invalid_filename)
    
    def test_get_upload_url_returns_correct_url(self, storage_service):
        """Test that get_upload_url returns the correct URL path."""
        filename = "test_image.jpg"
        url = storage_service.get_upload_url(filename)
        
        assert url == f"/{storage_service.uploads_dir}/{filename}"
    
    def test_get_result_url_returns_correct_url(self, storage_service):
        """Test that get_result_url returns the correct URL path."""
        filename = "heatmap_123.jpg"
        url = storage_service.get_result_url(filename)
        
        assert url == f"/{storage_service.results_dir}/{filename}"
    
    def test_get_upload_url_with_various_filenames(self, storage_service):
        """Test URL generation with various filename patterns."""
        test_cases = [
            "simple.jpg",
            "12345678-image.png",
            "product_ABC_123.jpeg",
            "file-with-dashes.jpg"
        ]
        
        for filename in test_cases:
            url = storage_service.get_upload_url(filename)
            assert url.endswith(filename)
            assert url.startswith("/")
    
    def test_get_result_url_with_various_filenames(self, storage_service):
        """Test result URL generation with various filename patterns."""
        test_cases = [
            "heatmap_1.jpg",
            "result_ABC123.png",
            "analysis-output.jpeg"
        ]
        
        for filename in test_cases:
            url = storage_service.get_result_url(filename)
            assert url.endswith(filename)
            assert url.startswith("/")
