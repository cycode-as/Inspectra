"""
Unit tests for ImageValidator service.

Tests validation logic for file format, size, and filename generation.
"""

import pytest
from io import BytesIO
from fastapi import UploadFile
from app.services.validation import ImageValidator


class TestImageValidator:
    """Test suite for ImageValidator class."""
    
    def create_mock_upload_file(self, filename: str, content_size: int) -> UploadFile:
        """
        Helper to create a mock UploadFile for testing.
        
        Args:
            filename: Name of the file
            content_size: Size of file content in bytes
        
        Returns:
            UploadFile: Mock upload file object
        """
        content = b"x" * content_size
        file = BytesIO(content)
        return UploadFile(filename=filename, file=file)
    
    def test_validate_image_with_valid_png(self):
        """Test validation passes for valid PNG file."""
        file = self.create_mock_upload_file("test.png", 1024)
        ImageValidator.validate_image(file)  # Should not raise
    
    def test_validate_image_with_valid_jpg(self):
        """Test validation passes for valid JPG file."""
        file = self.create_mock_upload_file("test.jpg", 1024)
        ImageValidator.validate_image(file)  # Should not raise
    
    def test_validate_image_with_valid_jpeg(self):
        """Test validation passes for valid JPEG file."""
        file = self.create_mock_upload_file("test.jpeg", 1024)
        ImageValidator.validate_image(file)  # Should not raise
    
    def test_validate_image_with_uppercase_extension(self):
        """Test validation passes for uppercase extension."""
        file = self.create_mock_upload_file("test.PNG", 1024)
        ImageValidator.validate_image(file)  # Should not raise
    
    def test_validate_image_with_mixed_case_extension(self):
        """Test validation passes for mixed case extension."""
        file = self.create_mock_upload_file("test.JpG", 1024)
        ImageValidator.validate_image(file)  # Should not raise
    
    def test_validate_image_rejects_invalid_extension(self):
        """Test validation rejects files with invalid extensions."""
        file = self.create_mock_upload_file("test.txt", 1024)
        with pytest.raises(ValueError, match="Invalid file format"):
            ImageValidator.validate_image(file)
    
    def test_validate_image_rejects_pdf(self):
        """Test validation rejects PDF files."""
        file = self.create_mock_upload_file("document.pdf", 1024)
        with pytest.raises(ValueError, match="Invalid file format"):
            ImageValidator.validate_image(file)
    
    def test_validate_image_rejects_oversized_file(self):
        """Test validation rejects files exceeding MAX_FILE_SIZE."""
        # Create file larger than 10 MB
        oversized_file = self.create_mock_upload_file("large.jpg", 11 * 1024 * 1024)
        with pytest.raises(ValueError, match="File size exceeds maximum"):
            ImageValidator.validate_image(oversized_file)
    
    def test_validate_image_accepts_max_size_file(self):
        """Test validation accepts file at exactly MAX_FILE_SIZE."""
        # Create file exactly 10 MB
        max_size_file = self.create_mock_upload_file("max.jpg", 10 * 1024 * 1024)
        ImageValidator.validate_image(max_size_file)  # Should not raise
    
    def test_validate_image_rejects_no_filename(self):
        """Test validation rejects file with no filename."""
        file = self.create_mock_upload_file("", 1024)
        file.filename = None
        with pytest.raises(ValueError, match="No filename provided"):
            ImageValidator.validate_image(file)
    
    def test_get_file_extension_with_single_dot(self):
        """Test extraction of extension from filename with single dot."""
        assert ImageValidator.get_file_extension("image.jpg") == "jpg"
    
    def test_get_file_extension_with_multiple_dots(self):
        """Test extraction of extension from filename with multiple dots."""
        assert ImageValidator.get_file_extension("my.image.file.png") == "png"
    
    def test_get_file_extension_with_no_extension(self):
        """Test extraction returns empty string for filename without extension."""
        assert ImageValidator.get_file_extension("imagefile") == ""
    
    def test_get_file_extension_preserves_case(self):
        """Test extraction preserves the case of extension."""
        assert ImageValidator.get_file_extension("image.PNG") == "PNG"
        assert ImageValidator.get_file_extension("image.JpG") == "JpG"
    
    def test_generate_unique_filename_preserves_extension(self):
        """Test unique filename generation preserves original extension."""
        original = "photo.jpg"
        unique = ImageValidator.generate_unique_filename(original)
        
        # Check extension is preserved
        assert unique.endswith(".jpg")
        # Check it's not the original filename
        assert unique != original
    
    def test_generate_unique_filename_preserves_case(self):
        """Test unique filename generation preserves extension case."""
        original = "photo.PNG"
        unique = ImageValidator.generate_unique_filename(original)
        
        assert unique.endswith(".PNG")
    
    def test_generate_unique_filename_creates_different_names(self):
        """Test unique filename generation creates different names each time."""
        original = "photo.jpg"
        unique1 = ImageValidator.generate_unique_filename(original)
        unique2 = ImageValidator.generate_unique_filename(original)
        
        # Should generate different filenames
        assert unique1 != unique2
    
    def test_generate_unique_filename_with_no_extension(self):
        """Test unique filename generation for file without extension."""
        original = "noextension"
        unique = ImageValidator.generate_unique_filename(original)
        
        # Should still generate a unique name (UUID only)
        assert unique != original
        assert "." not in unique
    
    def test_generate_unique_filename_with_multiple_dots(self):
        """Test unique filename generation preserves only the last extension."""
        original = "my.photo.file.jpeg"
        unique = ImageValidator.generate_unique_filename(original)
        
        assert unique.endswith(".jpeg")
    
    def test_allowed_extensions_constant(self):
        """Test ALLOWED_EXTENSIONS contains expected values."""
        assert ImageValidator.ALLOWED_EXTENSIONS == {"png", "jpg", "jpeg"}
    
    def test_max_file_size_constant(self):
        """Test MAX_FILE_SIZE is set to 10 MB."""
        assert ImageValidator.MAX_FILE_SIZE == 10 * 1024 * 1024
