"""
Inspection Schema Models

Pydantic models for request/response validation in inspection endpoints.
Includes field validators for anomaly scores, status values, and file paths.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Literal, Optional
import os


class InspectionCreate(BaseModel):
    """
    Schema for creating a new inspection record.
    
    Attributes:
        product_id: Product identifier (1-255 characters)
        image_path: Path to uploaded image file
        heatmap_path: Path to generated heatmap file
        anomaly_score: Defect confidence score (0.0-1.0)
        status: Inspection result classification
        inference_time_ms: AI inference duration in milliseconds
    """
    product_id: str = Field(..., min_length=1, max_length=255)
    image_path: str
    heatmap_path: str
    anomaly_score: float = Field(..., ge=0.0, le=1.0)
    status: Literal["PASS", "REJECT", "REVIEW"]
    inference_time_ms: int = Field(..., gt=0)
    
    @field_validator('anomaly_score')
    @classmethod
    def validate_anomaly_score(cls, v: float) -> float:
        """
        Validate anomaly_score is within valid range [0.0, 1.0].
        
        Args:
            v: The anomaly score value to validate
            
        Returns:
            The validated anomaly score
            
        Raises:
            ValueError: If score is outside [0.0, 1.0] range
        """
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"anomaly_score must be between 0.0 and 1.0, got {v}")
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """
        Validate status is one of the allowed values.
        
        Args:
            v: The status value to validate
            
        Returns:
            The validated status
            
        Raises:
            ValueError: If status is not PASS, REJECT, or REVIEW
        """
        allowed_statuses = {"PASS", "REJECT", "REVIEW"}
        if v not in allowed_statuses:
            raise ValueError(f"status must be one of {allowed_statuses}, got '{v}'")
        return v
    
    @field_validator('inference_time_ms')
    @classmethod
    def validate_inference_time(cls, v: int) -> int:
        """
        Validate inference_time_ms is a positive integer.
        
        Args:
            v: The inference time value to validate
            
        Returns:
            The validated inference time
            
        Raises:
            ValueError: If inference time is not positive
        """
        if v <= 0:
            raise ValueError(f"inference_time_ms must be positive, got {v}")
        return v


class InspectionResponse(BaseModel):
    """
    Schema for inspection API responses.
    
    Attributes:
        id: Unique inspection record identifier
        product_id: Product identifier
        image_url: Full URL to uploaded image
        heatmap_url: Full URL to heatmap image
        anomaly_score: Defect confidence score (0.0-1.0)
        status: Inspection result classification
        inference_time_ms: AI inference duration in milliseconds
        created_at: Timestamp of inspection creation
    """
    id: int
    product_id: str
    image_url: str
    heatmap_url: str
    anomaly_score: float
    status: Literal["PASS", "REJECT", "REVIEW"]
    inference_time_ms: int
    created_at: datetime
    
    # Configure to work with SQLAlchemy ORM models
    model_config = ConfigDict(from_attributes=True)


class PredictionResult(BaseModel):
    """
    Schema for AI inference prediction results.
    
    Attributes:
        anomaly_score: Defect confidence score (0.0-1.0)
        status: Inspection result classification
        heatmap_path: Path to generated heatmap file
        inference_time_ms: AI inference duration in milliseconds
    """
    anomaly_score: float = Field(..., ge=0.0, le=1.0)
    status: Literal["PASS", "REJECT", "REVIEW"]
    heatmap_path: str
    inference_time_ms: int = Field(..., gt=0)
    
    @field_validator('anomaly_score')
    @classmethod
    def validate_anomaly_score(cls, v: float) -> float:
        """
        Validate anomaly_score is within valid range [0.0, 1.0].
        
        Args:
            v: The anomaly score value to validate
            
        Returns:
            The validated anomaly score
            
        Raises:
            ValueError: If score is outside [0.0, 1.0] range
        """
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"anomaly_score must be between 0.0 and 1.0, got {v}")
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """
        Validate status is one of the allowed values.
        
        Args:
            v: The status value to validate
            
        Returns:
            The validated status
            
        Raises:
            ValueError: If status is not PASS, REJECT, or REVIEW
        """
        allowed_statuses = {"PASS", "REJECT", "REVIEW"}
        if v not in allowed_statuses:
            raise ValueError(f"status must be one of {allowed_statuses}, got '{v}'")
        return v
    
    @field_validator('heatmap_path')
    @classmethod
    def validate_heatmap_exists(cls, v: str) -> str:
        """
        Validate heatmap_path points to an existing file.
        
        Args:
            v: The file path to validate
            
        Returns:
            The validated file path
            
        Raises:
            ValueError: If file does not exist at specified path
        """
        if not os.path.exists(v):
            raise ValueError(f"Heatmap file not found: {v}")
        return v
    
    @field_validator('inference_time_ms')
    @classmethod
    def validate_inference_time(cls, v: int) -> int:
        """
        Validate inference_time_ms is a positive integer.
        
        Args:
            v: The inference time value to validate
            
        Returns:
            The validated inference time
            
        Raises:
            ValueError: If inference time is not positive
        """
        if v <= 0:
            raise ValueError(f"inference_time_ms must be positive, got {v}")
        return v


class ErrorResponse(BaseModel):
    """
    Schema for error responses.
    
    Attributes:
        error: Error message
        detail: Optional detailed error information
    """
    error: str
    detail: Optional[str] = None
