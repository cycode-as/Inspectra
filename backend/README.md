# INSPECTRA FastAPI Backend

AI-powered defect detection backend for product images. This FastAPI application provides REST API endpoints for uploading product images, performing automated quality inspection using AI inference, and storing inspection records in a PostgreSQL database.

## Features

✅ **Image Upload & Validation** - PNG, JPG, JPEG support with 10MB size limit
✅ **AI-Powered Inspection** - Automated defect detection with anomaly scoring
✅ **Database Persistence** - Complete inspection history in PostgreSQL/SQLite
✅ **RESTful API** - Three endpoints for inspection creation and retrieval
✅ **Static File Serving** - Direct HTTP access to uploaded images and heatmaps
✅ **Error Handling** - Consistent JSON error responses
✅ **Auto Documentation** - Interactive API docs via Swagger UI

## Project Structure

```
backend/
├── app/
│   ├── database.py             # Database connection & session management
│   ├── models/
│   │   └── inspection.py       # Inspection ORM model
│   ├── repositories/
│   │   └── inspection.py       # Repository pattern for DB operations
│   ├── schemas/
│   │   └── inspection.py       # Pydantic validation schemas
│   ├── services/
│   │   ├── inference.py        # AI inference service wrapper
│   │   ├── inspection.py       # Business logic orchestration
│   │   ├── storage.py          # File storage service
│   │   └── validation.py       # Image validation service
│   ├── routers/
│   │   └── inspections.py      # API endpoint definitions
│   └── middleware/
│       └── error_handlers.py   # Global error handlers
├── tests/                      # Unit and integration tests
├── uploads/                    # Directory for uploaded images
├── results/                    # Directory for heatmap results
├── main.py                     # FastAPI application entry point
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
└── .env.example               # Environment configuration template
```

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 12+ (optional, SQLite used by default for development)
- Virtual environment (venv)

### Installation

1. **Navigate to backend directory**:
   ```powershell
   cd backend
   ```

2. **Create and activate virtual environment** (if not already done):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```powershell
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**:
   ```powershell
   python main.py
   ```

   The API will be available at `http://localhost:8000`

### Running Tests

```powershell
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_basic_setup.py

# Run with coverage report
pytest --cov=app --cov-report=html
```

## API Documentation

Once the application is running, interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

#### POST /inspect

Upload and inspect a product image.

**Request**:
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Body**:
  - `file`: Image file (PNG/JPG/JPEG, max 10MB)
  - `product_id`: Product identifier (string)

**Response** (200 OK):
```json
{
  "id": 1,
  "product_id": "PROD-123",
  "image_url": "/uploads/uuid.jpg",
  "heatmap_url": "/results/heatmap_uuid.jpg",
  "anomaly_score": 0.75,
  "status": "REVIEW",
  "inference_time_ms": 150,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid file format or size
- `500 Internal Server Error`: Inference or database failure

#### GET /inspections

Retrieve all inspection records (ordered by created_at DESC).

**Response** (200 OK):
```json
[
  {
    "id": 3,
    "product_id": "PROD-789",
    "image_url": "/uploads/image3.jpg",
    "heatmap_url": "/results/heatmap3.jpg",
    "anomaly_score": 0.95,
    "status": "REJECT",
    "inference_time_ms": 200,
    "created_at": "2024-01-15T14:30:00Z"
  },
  {
    "id": 2,
    "product_id": "PROD-456",
    "image_url": "/uploads/image2.jpg",
    "heatmap_url": "/results/heatmap2.jpg",
    "anomaly_score": 0.15,
    "status": "PASS",
    "inference_time_ms": 100,
    "created_at": "2024-01-15T10:15:00Z"
  }
]
```

#### GET /inspections/{id}

Retrieve a single inspection record by ID.

**Response** (200 OK):
```json
{
  "id": 1,
  "product_id": "PROD-123",
  "image_url": "/uploads/uuid.jpg",
  "heatmap_url": "/results/heatmap_uuid.jpg",
  "anomaly_score": 0.75,
  "status": "REVIEW",
  "inference_time_ms": 150,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses**:
- `404 Not Found`: Inspection ID doesn't exist
- `400 Bad Request`: Invalid ID format

#### GET /health

Health check endpoint.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "inspectra-api"
}
```

### Static File Access

- **Uploaded Images**: `GET /uploads/{filename}`
- **Heatmap Results**: `GET /results/{filename}`

## Configuration

Configuration is managed through environment variables or a `.env` file. See `.env.example` for available options:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./inspectra.db` |
| `MAX_FILE_SIZE` | Maximum upload size in bytes | `10485760` (10MB) |
| `ALLOWED_EXTENSIONS` | Comma-separated file extensions | `png,jpg,jpeg` |
| `UPLOADS_DIR` | Directory for uploaded images | `uploads` |
| `RESULTS_DIR` | Directory for result heatmaps | `results` |
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |

### Database Configuration

**Development (SQLite)**:
```
DATABASE_URL=sqlite:///./inspectra.db
```

**Production (PostgreSQL)**:
```
DATABASE_URL=postgresql://username:password@hostname:5432/database_name
```

## Architecture

### Layered Architecture

1. **API Layer** (`routers/`) - HTTP request handling and response formatting
2. **Service Layer** (`services/`) - Business logic orchestration
3. **Repository Layer** (`repositories/`) - Database access abstraction
4. **Data Layer** (`models/`) - ORM models and database schema

### Key Components

- **InferenceService**: Wraps AI prediction function with validation
- **InspectionService**: Orchestrates complete inspection workflow
- **FileStorageService**: Manages file system operations
- **ImageValidator**: Validates upload format and size
- **InspectionRepository**: Handles database CRUD operations

## Testing

The project includes comprehensive test coverage:

- **Unit Tests**: Individual component testing (67+ tests)
- **Integration Tests**: End-to-end workflow testing
- **Property-Based Tests**: Hypothesis-based testing for edge cases

## Error Handling

All errors return consistent JSON format:

```json
{
  "error": "Error category",
  "detail": "Detailed error message"
}
```

**Error Categories**:
- `Validation failed` (400) - Invalid input data
- `Inference failed` (500) - AI prediction errors
- `Database operation failed` (500) - Database errors
- `Internal server error` (500) - Unexpected errors

## Development Status

✅ **Phase 1**: Project structure and dependencies
✅ **Phase 2**: Database layer with SQLAlchemy ORM
✅ **Phase 3**: Pydantic schemas and validation
✅ **Phase 4**: File storage and validation services
✅ **Phase 5**: AI inference service integration
✅ **Phase 6**: Business logic service layer
✅ **Phase 7**: REST API endpoints
✅ **Phase 8**: Static file serving
✅ **Phase 9**: Global error handlers
✅ **Phase 10**: Documentation and configuration

**Status**: Production-ready MVP complete! 🚀

## Deployment

### Using Uvicorn (Development)

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Using Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

- Use PostgreSQL instead of SQLite
- Configure CORS origins appropriately
- Enable HTTPS/TLS
- Set up proper logging and monitoring
- Use environment-specific configuration
- Implement rate limiting
- Add authentication/authorization if needed

## License

[Add license information]

## Contact

[Add contact information]

## Next Steps

- [ ] Add authentication and authorization
- [ ] Implement rate limiting
- [ ] Add request logging middleware
- [ ] Set up monitoring and alerting
- [ ] Add database migrations with Alembic
- [ ] Implement file cleanup for orphaned files
- [ ] Add batch inspection endpoint
- [ ] Create Docker deployment configuration
- [ ] Set up CI/CD pipeline
- [ ] Add performance optimization

---

Built with ❤️ using FastAPI, SQLAlchemy, and PostgreSQL
