"""
Basic Setup Tests

Verify that the basic project structure and configuration are working correctly.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from config import get_settings


def test_health_check():
    """Test the health check endpoint returns correct status."""
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "inspectra-api"}


def test_settings_load():
    """Test that configuration settings load correctly."""
    settings = get_settings()
    
    assert settings is not None
    assert settings.max_file_size == 10 * 1024 * 1024  # 10 MB
    assert "png" in settings.allowed_extensions
    assert "jpg" in settings.allowed_extensions
    assert "jpeg" in settings.allowed_extensions
    assert settings.uploads_dir == "uploads"
    assert settings.results_dir == "results"


def test_directories_exist():
    """Test that required directories exist."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    uploads_dir = os.path.join(backend_dir, "uploads")
    results_dir = os.path.join(backend_dir, "results")
    app_dir = os.path.join(backend_dir, "app")
    tests_dir = os.path.join(backend_dir, "tests")
    
    assert os.path.exists(uploads_dir), "uploads directory should exist"
    assert os.path.exists(results_dir), "results directory should exist"
    assert os.path.exists(app_dir), "app directory should exist"
    assert os.path.exists(tests_dir), "tests directory should exist"


def test_app_metadata():
    """Test that FastAPI app has correct metadata."""
    assert app.title == "INSPECTRA API"
    assert app.version == "1.0.0"
    assert "defect detection" in app.description.lower()
