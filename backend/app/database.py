"""
Database Connection and Session Management Module

Provides SQLAlchemy engine setup, session management, and database
initialization logic. Supports PostgreSQL (primary) and SQLite (development fallback).
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.engine import Engine
from typing import Generator
import logging

from config import get_settings

# Configure logging
logger = logging.getLogger(__name__)

# Get application settings
settings = get_settings()

# Create SQLAlchemy engine
# - For PostgreSQL: Uses connection pooling with pool_pre_ping for connection health checks
# - For SQLite: Uses check_same_thread=False to allow multi-threaded access in development
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        echo=False  # Set to True for SQL query logging during development
    )
    logger.info(f"Using SQLite database: {settings.database_url}")
else:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=5,         # Number of connections to maintain
        max_overflow=10,     # Maximum number of connections to create beyond pool_size
        echo=False           # Set to True for SQL query logging during development
    )
    logger.info(f"Using PostgreSQL database")


# Enable foreign key constraints for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Enable foreign key constraints for SQLite databases.
    
    This event listener is triggered on every database connection.
    For SQLite, it enables foreign key constraint checking which is
    disabled by default.
    
    Args:
        dbapi_conn: Database API connection object
        connection_record: Connection record from the pool
    """
    if settings.database_url.startswith("sqlite"):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Create session factory
# SessionLocal is a factory for creating database sessions
SessionLocal = sessionmaker(
    autocommit=False,  # Explicit transaction control
    autoflush=False,   # Manual flush control for better performance
    bind=engine
)

# Create declarative base for ORM models
# All ORM models should inherit from this Base class
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI dependency injection.
    
    Creates a new SQLAlchemy session for each request and ensures
    proper cleanup after the request completes. This function should
    be used with FastAPI's Depends() for automatic session management.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.
    
    This function creates all tables defined in ORM models that inherit
    from Base. It should be called during application startup to ensure
    the database schema is properly initialized.
    
    If tables already exist, this function does nothing (it won't drop
    or modify existing tables).
    
    Note:
        This is suitable for development and simple deployments.
        For production, consider using Alembic for database migrations.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def check_db_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Attempts to connect to the database and execute a simple query
    to verify connectivity. Useful for health checks and startup validation.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        db = SessionLocal()
        # Execute a simple query to test connection
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection check successful")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


def get_engine() -> Engine:
    """
    Get the SQLAlchemy engine instance.
    
    Useful for advanced database operations or when direct engine
    access is needed (e.g., for running raw SQL queries).
    
    Returns:
        Engine: SQLAlchemy engine instance
    """
    return engine
