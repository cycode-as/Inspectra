"""
Inspection ORM Model

Defines the SQLAlchemy ORM model for inspection records in the database.
Each inspection represents a single product image analysis with AI inference results.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base


class Inspection(Base):
    """
    Inspection database model.
    
    Stores the results of AI-powered defect detection for product images.
    Each record contains the inspection metadata, inference results, and
    file paths to the uploaded image and generated heatmap.
    
    Attributes:
        id (int): Primary key, auto-incrementing inspection identifier
        product_id (str): Product identifier from upload form data
        image_path (str): Path to the uploaded product image
        heatmap_path (str): Path to the generated heatmap image (nullable)
        anomaly_score (float): AI confidence score for defect detection (0.0-1.0)
        status (str): Classification result (PASS, REJECT, or REVIEW)
        inference_time_ms (int): AI inference execution time in milliseconds
        created_at (datetime): Timestamp of inspection creation (auto-generated)
    """
    
    __tablename__ = "inspections"
    
    # Primary key with auto-increment
    id = Column(
        Integer, 
        primary_key=True, 
        index=True, 
        autoincrement=True,
        comment="Unique inspection identifier"
    )
    
    # Product identifier
    product_id = Column(
        String(255), 
        nullable=False, 
        index=True,
        comment="Product identifier from upload"
    )
    
    # Image file path
    image_path = Column(
        String(512), 
        nullable=False,
        comment="Path to uploaded product image"
    )
    
    # Heatmap file path (nullable as it may not always be generated)
    heatmap_path = Column(
        String(512), 
        nullable=True,
        comment="Path to generated heatmap visualization"
    )
    
    # AI inference results
    anomaly_score = Column(
        Float, 
        nullable=False,
        comment="Anomaly detection confidence score (0.0-1.0)"
    )
    
    status = Column(
        String(20), 
        nullable=False, 
        index=True,
        comment="Inspection status: PASS, REJECT, or REVIEW"
    )
    
    inference_time_ms = Column(
        Integer, 
        nullable=False,
        comment="AI inference execution time in milliseconds"
    )
    
    # Timestamp with automatic default value
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False, 
        index=True,
        comment="Timestamp of inspection creation"
    )
    
    # Additional indexes for query optimization
    __table_args__ = (
        # Composite index for querying by product and status
        Index('idx_product_status', 'product_id', 'status'),
        # Index for ordering by creation time (already indexed above, but explicit for clarity)
        Index('idx_created_at_desc', 'created_at', postgresql_ops={'created_at': 'DESC'}),
    )
    
    def __repr__(self) -> str:
        """String representation of Inspection instance."""
        return (
            f"<Inspection(id={self.id}, "
            f"product_id='{self.product_id}', "
            f"status='{self.status}', "
            f"anomaly_score={self.anomaly_score:.3f}, "
            f"created_at={self.created_at})>"
        )
