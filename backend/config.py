"""
Configuration Management Module

Manages environment-based configuration for database connections,
file storage settings, and validation parameters using Pydantic Settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    
    Attributes:
        database_url: PostgreSQL connection string (defaults to SQLite for development)
        max_file_size: Maximum upload file size in bytes (default: 10 MB)
        allowed_extensions: List of allowed image file extensions
        uploads_dir: Directory path for uploaded images
        results_dir: Directory path for result heatmaps
    """
    
    # Database Configuration
    database_url: str = "sqlite:///./inspectra.db"
    
    # File Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10 MB in bytes
    allowed_extensions: List[str] = ["png", "jpg", "jpeg"]
    
    # Directory Configuration
    uploads_dir: str = "uploads"
    results_dir: str = "results"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Dependency injection function for settings.
    
    Returns:
        Settings: Application settings instance
    """
    return settings
