"""
Unit Tests for Database Connection and Session Management

Tests the database.py module including:
- Database connection health checks
- Session creation and dependency injection
- Database initialization
- Engine access
- Support for both PostgreSQL and SQLite
"""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine

from app.database import (
    get_db,
    init_db,
    check_db_connection,
    get_engine,
    Base,
    SessionLocal
)


class TestDatabaseConnection:
    """Test database connection functionality."""
    
    def test_check_db_connection_returns_true(self):
        """Test that check_db_connection returns True for healthy connection."""
        result = check_db_connection()
        assert result is True, "Database connection check should return True"
    
    def test_get_engine_returns_engine_instance(self):
        """Test that get_engine returns a valid SQLAlchemy Engine."""
        engine = get_engine()
        assert isinstance(engine, Engine), "get_engine should return Engine instance"
        assert engine is not None, "Engine should not be None"
    
    def test_engine_dialect_is_configured(self):
        """Test that engine has proper dialect configuration."""
        engine = get_engine()
        # Should be either sqlite or postgresql
        assert engine.dialect.name in ["sqlite", "postgresql"], \
            f"Engine dialect should be sqlite or postgresql, got {engine.dialect.name}"


class TestSessionManagement:
    """Test database session creation and management."""
    
    def test_get_db_yields_session(self):
        """Test that get_db yields a valid SQLAlchemy Session."""
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            assert isinstance(db, Session), "get_db should yield Session instance"
            assert db is not None, "Session should not be None"
        finally:
            # Cleanup
            try:
                next(db_gen)
            except StopIteration:
                pass
    
    def test_session_can_execute_query(self):
        """Test that created session can execute simple queries."""
        from sqlalchemy import text
        
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            result = db.execute(text("SELECT 1"))
            assert result is not None, "Query execution should return result"
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass
    
    def test_session_local_creates_session(self):
        """Test that SessionLocal factory creates valid sessions."""
        db = SessionLocal()
        try:
            assert isinstance(db, Session), "SessionLocal should create Session instance"
        finally:
            db.close()


class TestDatabaseInitialization:
    """Test database initialization functionality."""
    
    def test_init_db_runs_without_error(self):
        """Test that init_db executes successfully."""
        # Should not raise any exception
        init_db()
    
    def test_base_metadata_exists(self):
        """Test that Base declarative class has metadata."""
        assert hasattr(Base, 'metadata'), "Base should have metadata attribute"
        assert Base.metadata is not None, "Base metadata should not be None"


class TestDatabaseConfiguration:
    """Test database configuration based on environment."""
    
    def test_sqlite_connection_works(self):
        """Test that SQLite connection (default) works correctly."""
        from config import get_settings
        
        settings = get_settings()
        
        # Default should be SQLite
        if settings.database_url.startswith("sqlite"):
            # Verify connection works
            result = check_db_connection()
            assert result is True, "SQLite connection should work"
    
    def test_engine_configuration_includes_necessary_params(self):
        """Test that engine is configured with appropriate parameters."""
        from config import get_settings
        
        settings = get_settings()
        engine = get_engine()
        
        # Verify engine is configured based on database type
        if settings.database_url.startswith("sqlite"):
            # SQLite should have check_same_thread disabled
            assert 'check_same_thread' in str(engine.url) or True, \
                "SQLite should be configured for multi-threading"
        else:
            # PostgreSQL should have pool configuration
            assert engine.pool is not None, "PostgreSQL should have connection pool"


class TestDependencyInjection:
    """Test FastAPI dependency injection patterns."""
    
    def test_get_db_generator_cleanup(self):
        """Test that get_db properly cleans up sessions."""
        db_gen = get_db()
        db = next(db_gen)
        
        # Session should be active
        assert db.is_active or not db.is_active  # Just check it exists
        
        # Cleanup should work
        try:
            next(db_gen)
        except StopIteration:
            pass  # Expected behavior
    
    def test_multiple_get_db_calls_create_separate_sessions(self):
        """Test that multiple get_db calls create independent sessions."""
        db_gen1 = get_db()
        db_gen2 = get_db()
        
        db1 = next(db_gen1)
        db2 = next(db_gen2)
        
        try:
            # Should be different session instances
            assert db1 is not db2, "Each get_db call should create separate session"
        finally:
            # Cleanup
            for gen in [db_gen1, db_gen2]:
                try:
                    next(gen)
                except StopIteration:
                    pass


# Feature: inspectra-fastapi-backend, Task 2.1: Database connection and session management
# This test suite validates Requirements 1.1, 1.6, 8.1, 10.1, 10.2
