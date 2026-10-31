# Requirements Document

## Introduction

INSPECTRA is an AI-powered defect-detection system backend that receives uploaded images, performs automated quality inspection using AI inference, stores inspection records in a PostgreSQL database, and serves inspection data and images to a frontend application. The system validates image uploads, processes them through a pre-existing AI inference function, and maintains a complete history of inspections with anomaly scores and pass/fail/review status classifications.

## Glossary

- **Backend_API**: The FastAPI application server that handles HTTP requests
- **Database**: PostgreSQL database accessed via SQLAlchemy ORM
- **Inspection_Record**: A database record containing inspection metadata and results
- **Image_Validator**: Component that validates uploaded image files
- **Inference_Service**: Service that calls the pre-existing AI prediction function
- **Static_File_Server**: FastAPI component that serves uploaded and result images
- **Upload**: Multipart form data containing an image file and product identifier
- **Anomaly_Score**: Float value representing the confidence level of defect detection
- **Status**: Classification result with values PASS, REJECT, or REVIEW
- **Heatmap**: Visual representation of detected anomalies in the inspected image

## Requirements

### Requirement 1: Application Initialization

**User Story:** As a system administrator, I want the backend to initialize with proper database connectivity and directory structure, so that the application can handle inspection requests reliably.

#### Acceptance Criteria

1. WHEN the Backend_API starts, THE Backend_API SHALL establish a connection to the PostgreSQL Database
2. WHEN the Backend_API starts, THE Backend_API SHALL create the uploads directory if it does not exist
3. WHEN the Backend_API starts, THE Backend_API SHALL create the results directory if it does not exist
4. WHEN the Backend_API starts, THE Backend_API SHALL mount the uploads directory as a static file path
5. WHEN the Backend_API starts, THE Backend_API SHALL mount the results directory as a static file path
6. WHEN the Backend_API starts, THE Backend_API SHALL create database tables if they do not exist

### Requirement 2: Image Upload and Validation

**User Story:** As a quality control operator, I want to upload product images for inspection, so that defects can be automatically detected.

#### Acceptance Criteria

1. WHEN a POST request is received at /inspect with multipart form data, THE Backend_API SHALL accept the request
2. WHEN an uploaded file is received, THE Image_Validator SHALL verify the file format is PNG, JPG, or JPEG
3. WHEN an uploaded file exceeds 10 MB, THE Image_Validator SHALL reject the file with an error message
4. WHEN an uploaded file has an unsupported format, THE Image_Validator SHALL reject the file with an error message
5. WHEN an uploaded file passes validation, THE Backend_API SHALL save the file to the uploads directory with a unique filename
6. WHEN saving an uploaded file, THE Backend_API SHALL preserve the original file extension

### Requirement 3: AI Inference Integration

**User Story:** As a quality control operator, I want uploaded images to be analyzed by AI, so that defects are detected automatically without manual inspection.

#### Acceptance Criteria

1. WHEN a valid image is saved to the uploads directory, THE Inference_Service SHALL call the predict function with the image path
2. WHEN the predict function is called, THE Inference_Service SHALL receive a dictionary containing anomaly_score, status, heatmap_path, and inference_time_ms
3. WHEN the predict function returns results, THE Inference_Service SHALL validate that anomaly_score is a float between 0.0 and 1.0
4. WHEN the predict function returns results, THE Inference_Service SHALL validate that status is one of PASS, REJECT, or REVIEW
5. WHEN the predict function returns results, THE Inference_Service SHALL validate that heatmap_path points to an existing file
6. IF the predict function raises an exception, THEN THE Inference_Service SHALL log the error and return a descriptive error message

### Requirement 4: Inspection Record Persistence

**User Story:** As a quality manager, I want all inspection results stored in a database, so that I can track product quality over time.

#### Acceptance Criteria

1. WHEN AI inference completes successfully, THE Backend_API SHALL create an Inspection_Record in the Database
2. WHEN creating an Inspection_Record, THE Backend_API SHALL store the product_id from the upload form data
3. WHEN creating an Inspection_Record, THE Backend_API SHALL store the image_path pointing to the uploaded file
4. WHEN creating an Inspection_Record, THE Backend_API SHALL store the heatmap_path from the inference results
5. WHEN creating an Inspection_Record, THE Backend_API SHALL store the anomaly_score from the inference results
6. WHEN creating an Inspection_Record, THE Backend_API SHALL store the status from the inference results
7. WHEN creating an Inspection_Record, THE Backend_API SHALL store the inference_time_ms from the inference results
8. WHEN creating an Inspection_Record, THE Backend_API SHALL generate a unique integer id as the primary key
9. WHEN creating an Inspection_Record, THE Backend_API SHALL set created_at to the current timestamp
10. WHEN the Inspection_Record is successfully saved, THE Backend_API SHALL return the complete inspection data as JSON

### Requirement 5: Inspection History Retrieval

**User Story:** As a quality manager, I want to retrieve all inspection records, so that I can review the quality control history.

#### Acceptance Criteria

1. WHEN a GET request is received at /inspections, THE Backend_API SHALL retrieve all Inspection_Record entries from the Database
2. WHEN retrieving inspection records, THE Backend_API SHALL order results by created_at in descending order
3. WHEN inspection records are retrieved, THE Backend_API SHALL return them as a JSON array
4. WHEN no inspection records exist, THE Backend_API SHALL return an empty JSON array

### Requirement 6: Single Inspection Record Retrieval

**User Story:** As a quality manager, I want to retrieve a specific inspection by ID, so that I can review detailed results for a particular product.

#### Acceptance Criteria

1. WHEN a GET request is received at /inspections/{id}, THE Backend_API SHALL retrieve the Inspection_Record with the matching id from the Database
2. WHEN the requested inspection id exists, THE Backend_API SHALL return the Inspection_Record as JSON
3. WHEN the requested inspection id does not exist, THE Backend_API SHALL return a 404 status code with an error message
4. WHEN the id parameter is not a valid integer, THE Backend_API SHALL return a 400 status code with an error message

### Requirement 7: Static File Access

**User Story:** As a frontend developer, I want to access uploaded images and heatmaps via HTTP URLs, so that I can display them in the user interface.

#### Acceptance Criteria

1. WHEN a GET request is received for /uploads/{filename}, THE Static_File_Server SHALL serve the file from the uploads directory
2. WHEN a GET request is received for /results/{filename}, THE Static_File_Server SHALL serve the file from the results directory
3. WHEN a requested file does not exist, THE Static_File_Server SHALL return a 404 status code
4. WHEN a file is served, THE Static_File_Server SHALL set the appropriate Content-Type header based on the file extension

### Requirement 8: Database Schema Definition

**User Story:** As a backend developer, I want a well-defined database schema, so that inspection data is stored consistently and efficiently.

#### Acceptance Criteria

1. THE Database SHALL define an Inspection table with columns: id, product_id, image_path, heatmap_path, anomaly_score, status, inference_time_ms, created_at
2. THE Database SHALL define id as an auto-incrementing integer primary key
3. THE Database SHALL define product_id as a non-nullable string column
4. THE Database SHALL define image_path as a non-nullable string column
5. THE Database SHALL define heatmap_path as a nullable string column
6. THE Database SHALL define anomaly_score as a non-nullable float column
7. THE Database SHALL define status as a non-nullable string column
8. THE Database SHALL define inference_time_ms as a non-nullable integer column
9. THE Database SHALL define created_at as a non-nullable timestamp column with default value of current timestamp

### Requirement 9: Error Handling and Response Format

**User Story:** As a frontend developer, I want consistent error responses, so that I can handle errors gracefully in the user interface.

#### Acceptance Criteria

1. WHEN a validation error occurs, THE Backend_API SHALL return a JSON response with an error field containing the error message
2. WHEN a database error occurs, THE Backend_API SHALL return a 500 status code with a descriptive error message
3. WHEN a file operation fails, THE Backend_API SHALL return a 500 status code with a descriptive error message
4. WHEN inference fails, THE Backend_API SHALL return a 500 status code with a descriptive error message
5. WHEN a successful inspection completes, THE Backend_API SHALL return a 200 status code with the inspection data
6. WHEN inspection records are successfully retrieved, THE Backend_API SHALL return a 200 status code with the data array

### Requirement 10: Configuration Management

**User Story:** As a system administrator, I want database connection settings to be configurable, so that the application can be deployed in different environments.

#### Acceptance Criteria

1. THE Backend_API SHALL read the database connection string from environment variables or configuration files
2. WHEN the database connection string is not provided, THE Backend_API SHALL use a default SQLite connection for local development
3. THE Backend_API SHALL support configuration of maximum file upload size
4. THE Backend_API SHALL support configuration of allowed file extensions
5. THE Backend_API SHALL support configuration of upload and results directory paths
