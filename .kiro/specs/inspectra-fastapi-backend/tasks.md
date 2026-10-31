# Implementation Plan: INSPECTRA FastAPI Backend

## Overview

This implementation plan breaks down the INSPECTRA FastAPI backend into discrete, executable tasks. The backend provides an HTTP API for AI-powered defect detection in product images, integrating with a pre-existing AI inference function, PostgreSQL database, and local filesystem storage. The implementation follows a layered architecture with comprehensive property-based testing using Hypothesis.

## Tasks

- [x] 1. Set up project structure and core dependencies
  - Create FastAPI project directory structure with app/, tests/, uploads/, results/ folders
  - Create requirements.txt with FastAPI, SQLAlchemy, psycopg2-binary, Pydantic, python-multipart, Hypothesis, pytest, pytest-asyncio, httpx
  - Create main.py with basic FastAPI app initialization
  - Create config.py for environment-based configuration management
  - _Requirements: 1.1, 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 2. Implement database layer with SQLAlchemy ORM
  - [x] 2.1 Create database connection and session management
    - Implement database.py with SQLAlchemy engine setup
    - Add support for PostgreSQL (primary) and SQLite (development fallback)
    - Implement get_db() dependency for session injection
    - Add database initialization logic to create tables
    - _Requirements: 1.1, 1.6, 8.1, 10.1, 10.2_

  - [x] 2.2 Define Inspection ORM model
    - Create models/inspection.py with Inspection SQLAlchemy model
    - Define all columns: id (primary key, autoincrement), product_id, image_path, heatmap_path, anomaly_score, status, inference_time_ms, created_at
    - Add indexes on created_at, product_id, and status columns
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9_

  - [x] 2.3 Implement database repository pattern
    - Create repositories/inspection.py with InspectionRepository class
    - Implement create() method to insert new inspection records
    - Implement get_all() method to retrieve all records ordered by created_at DESC
    - Implement get_by_id() method to retrieve single record by ID
    - _Requirements: 4.1, 4.8, 5.1, 5.2, 6.1_

  - [ ]* 2.4 Write unit tests for repository operations
    - Test create() with valid inspection data
    - Test get_all() with multiple records and empty database
    - Test get_by_id() with existing and non-existent IDs
    - Use in-memory SQLite for test database
    - _Requirements: 4.1, 5.1, 6.1_

- [x] 3. Implement Pydantic schemas for request/response validation
  - Create schemas/inspection.py with InspectionCreate, InspectionResponse, PredictionResult, and ErrorResponse models
  - Add field validators for anomaly_score (0.0-1.0 range), status (PASS/REJECT/REVIEW), inference_time_ms (positive integer)
  - Add validator for heatmap_path to check file existence in PredictionResult
  - Configure orm_mode for InspectionResponse to work with SQLAlchemy models
  - _Requirements: 3.3, 3.4, 3.5, 4.10, 9.1_

- [x] 4. Implement file storage and validation services
  - [x] 4.1 Create file storage service
    - Create services/storage.py with FileStorageService class
    - Implement ensure_directories() to create uploads/ and results/ directories
    - Implement save_upload() to save uploaded files with unique filenames
    - Implement get_upload_url() and get_result_url() for URL generation
    - _Requirements: 1.2, 1.3, 2.5, 2.6_

  - [x] 4.2 Create image validation service
    - Create services/validation.py with ImageValidator class
    - Define ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"} and MAX_FILE_SIZE = 10 * 1024 * 1024
    - Implement validate_image() to check file format and size
    - Implement get_file_extension() and generate_unique_filename() utilities
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.6_

  - [ ]* 4.3 Write property test for file extension validation
    - **Property 1: File Extension Validation**
    - **Validates: Requirements 2.2, 2.4**
    - Use Hypothesis to generate random file extensions
    - Verify validator accepts only png/jpg/jpeg (case-insensitive) and rejects all others
    - _Requirements: 2.2, 2.4_

  - [ ]* 4.4 Write property test for unique filename generation
    - **Property 2: Unique Filename Generation Preserves Extension**
    - **Validates: Requirements 2.5, 2.6**
    - Use Hypothesis to generate random filenames with valid extensions
    - Verify generated unique filename preserves original extension
    - _Requirements: 2.5, 2.6_

- [x] 5. Checkpoint - Verify database and file handling
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement AI inference service integration
  - [x] 6.1 Create inference service wrapper
    - Create services/inference.py with InferenceService class
    - Accept predict_function as dependency injection parameter
    - Implement predict() method to call external AI function with image path
    - Implement validate_prediction_result() to check result structure and values
    - Add error handling to catch and wrap exceptions from AI function
    - _Requirements: 3.1, 3.2, 3.6_

  - [ ]* 6.2 Write property test for anomaly score validation
    - **Property 3: Anomaly Score Validation**
    - **Validates: Requirements 3.3**
    - Use Hypothesis to generate random float values
    - Verify validator accepts only values in [0.0, 1.0] range
    - _Requirements: 3.3_

  - [ ]* 6.3 Write property test for status validation
    - **Property 4: Status Validation**
    - **Validates: Requirements 3.4**
    - Use Hypothesis to generate random status strings
    - Verify validator accepts only "PASS", "REJECT", "REVIEW" (exact match)
    - _Requirements: 3.4_

  - [ ]* 6.4 Write property test for heatmap path validation
    - **Property 5: Heatmap Path Validation**
    - **Validates: Requirements 3.5**
    - Use Hypothesis to generate random file paths (some existing, some not)
    - Verify validator accepts only paths that point to existing files
    - _Requirements: 3.5_

  - [ ]* 6.5 Write unit tests for inference error handling
    - Test predict() with mock that raises exception
    - Verify error is logged and InferenceError is raised with descriptive message
    - _Requirements: 3.6_

- [x] 7. Implement business logic service layer
  - Create services/inspection.py with InspectionService class
  - Inject database session and InferenceService as dependencies
  - Implement process_inspection() method to orchestrate complete workflow
  - Coordinate between inference service, database repository, and file storage
  - Add transaction handling for database operations
  - Implement error recovery and cleanup on failure
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.9_

- [x] 8. Implement REST API endpoints
  - [x] 8.1 Create inspection endpoints router
    - Create routers/inspections.py with APIRouter
    - Implement POST /inspect endpoint accepting multipart form data
    - Implement GET /inspections endpoint to list all inspections
    - Implement GET /inspections/{id} endpoint to retrieve single inspection
    - Add proper dependency injection for database session
    - _Requirements: 2.1, 5.1, 6.1_

  - [x] 8.2 Configure static file serving
    - Mount /uploads path to uploads directory using FastAPI StaticFiles
    - Mount /results path to results directory using FastAPI StaticFiles
    - _Requirements: 1.4, 1.5, 7.1, 7.2, 7.3_

  - [x] 8.3 Implement global error handlers
    - Create middleware/error_handlers.py with exception handlers
    - Add handler for RequestValidationError returning 400 status
    - Add handler for custom InferenceError returning 500 status
    - Add handler for generic Exception returning 500 status
    - Ensure all error responses follow JSON format with "error" and "detail" fields
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 6.3, 6.4_

  - [ ]* 8.4 Write property test for inspection record persistence round-trip
    - **Property 6: Inspection Record Persistence Round-Trip**
    - **Validates: Requirements 4.1-4.10**
    - Use Hypothesis to generate random valid inspection data
    - Create inspection record in database, then retrieve by ID
    - Verify retrieved data matches original with additional id and created_at fields
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10_

  - [ ]* 8.5 Write property test for inspection ordering
    - **Property 7: Inspection Ordering**
    - **Validates: Requirements 5.2**
    - Use Hypothesis to generate multiple inspection records with different timestamps
    - Retrieve all inspections and verify they're ordered by created_at DESC
    - _Requirements: 5.2_

  - [ ]* 8.6 Write property test for inspection retrieval by ID
    - **Property 8: Inspection Retrieval by ID**
    - **Validates: Requirements 6.1, 6.2**
    - Use Hypothesis to generate random inspection records
    - Create records in database, verify each can be retrieved by its ID
    - _Requirements: 6.1, 6.2_

  - [ ]* 8.7 Write property test for non-existent ID returns 404
    - **Property 9: Non-Existent ID Returns 404**
    - **Validates: Requirements 6.3**
    - Use Hypothesis to generate random non-existent IDs
    - Attempt to retrieve each ID and verify 404 status code is returned
    - _Requirements: 6.3_

- [~] 9. Checkpoint - Verify API endpoints and error handling
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Implement static file serving tests
  - [ ]* 10.1 Write property test for static file serving
    - **Property 10: Static File Serving**
    - **Validates: Requirements 7.1, 7.2**
    - Use Hypothesis to generate random valid filenames
    - Create files in uploads and results directories
    - Verify files can be served via /uploads/{filename} and /results/{filename}
    - _Requirements: 7.1, 7.2_

  - [ ]* 10.2 Write property test for non-existent file returns 404
    - **Property 11: Non-Existent File Returns 404**
    - **Validates: Requirements 7.3**
    - Use Hypothesis to generate random non-existent filenames
    - Attempt to access files via static endpoints and verify 404 status
    - _Requirements: 7.3_

  - [ ]* 10.3 Write property test for Content-Type header correctness
    - **Property 12: Content-Type Header Correctness**
    - **Validates: Requirements 7.4**
    - Use Hypothesis to generate files with different image extensions (png, jpg, jpeg)
    - Serve files via static endpoints and verify Content-Type header matches extension
    - _Requirements: 7.4_

- [ ] 11. Implement error response format consistency
  - [ ]* 11.1 Write property test for error response format
    - **Property 13: Error Response Format Consistency**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4**
    - Use Hypothesis to generate various error scenarios (validation, database, file, inference)
    - Verify all error responses contain "error" field with descriptive message
    - Test across different error types to ensure consistency
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [ ] 12. Write integration tests for complete workflows
  - [ ]* 12.1 Write integration test for successful inspection flow
    - Test POST /inspect with valid image file and product_id
    - Verify 200 response with complete inspection data
    - Verify record is created in database
    - Verify uploaded file and heatmap are accessible via static URLs
    - _Requirements: 2.1, 4.1, 7.1, 7.2, 9.5_

  - [ ]* 12.2 Write integration test for inspection retrieval
    - Create multiple inspection records
    - Test GET /inspections returns all records ordered correctly
    - Test GET /inspections/{id} returns correct record
    - Verify empty array returned when no records exist
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 9.6_

  - [ ]* 12.3 Write integration test for validation errors
    - Test POST /inspect with invalid file format (e.g., .txt)
    - Test POST /inspect with file exceeding 10 MB
    - Verify 400 status with error message
    - _Requirements: 2.3, 2.4, 9.1_

  - [ ]* 12.4 Write integration test for error scenarios
    - Test GET /inspections/{id} with non-existent ID (verify 404)
    - Test GET /inspections/{id} with invalid ID format (verify 400)
    - Mock inference failure and verify 500 response
    - _Requirements: 6.3, 6.4, 9.4_

- [x] 13. Add application lifecycle and configuration
  - Implement startup event handler to initialize directories and database
  - Implement shutdown event handler for cleanup
  - Add health check endpoint GET /health
  - Add structured logging configuration using Python logging module
  - Add request logging middleware
  - Configure CORS middleware for frontend integration
  - _Requirements: 1.1, 1.2, 1.3, 1.6_

- [x] 14. Add documentation and deployment preparation
  - Configure FastAPI automatic OpenAPI documentation
  - Add docstrings to all public functions and classes
  - Create README.md with setup instructions, API documentation, and usage examples
  - Create .env.example file with all configuration variables
  - Add type hints to all function signatures
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 15. Final checkpoint - Complete system verification
  - Run all unit tests, property tests, and integration tests
  - Verify test coverage meets 85% goal
  - Test complete workflow end-to-end with sample images
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Property-based tests use Hypothesis library with minimum 100 iterations per test
- Each property test must include comment tag: `# Feature: inspectra-fastapi-backend, Property N: [property text]`
- Integration tests should use PostgreSQL test container for realistic testing
- All error responses must follow consistent JSON format: `{"error": "...", "detail": "..."}`
- Database operations should use repository pattern for testability
- External AI prediction function should be injected as dependency for mocking in tests
- Configuration should support both PostgreSQL (production) and SQLite (development) databases
- Static file serving is handled by FastAPI's StaticFiles middleware
- Checkpoints ensure incremental validation and provide natural stopping points for review

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2.1", "3"] },
    { "id": 2, "tasks": ["2.2", "4.1"] },
    { "id": 3, "tasks": ["2.3", "4.2"] },
    { "id": 4, "tasks": ["2.4", "4.3", "4.4"] },
    { "id": 5, "tasks": ["6.1"] },
    { "id": 6, "tasks": ["6.2", "6.3", "6.4", "6.5"] },
    { "id": 7, "tasks": ["7"] },
    { "id": 8, "tasks": ["8.1", "8.2"] },
    { "id": 9, "tasks": ["8.3"] },
    { "id": 10, "tasks": ["8.4", "8.5", "8.6", "8.7"] },
    { "id": 11, "tasks": ["10.1", "10.2", "10.3", "11.1"] },
    { "id": 12, "tasks": ["12.1", "12.2", "12.3", "12.4"] },
    { "id": 13, "tasks": ["13", "14"] }
  ]
}
```
