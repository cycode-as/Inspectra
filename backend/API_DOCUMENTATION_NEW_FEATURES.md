# INSPECTRA API Documentation - New Features

This document describes the newly implemented features for the INSPECTRA backend API.

## 📋 Table of Contents

1. [Feedback System](#feedback-system)
2. [Analytics & Reporting](#analytics--reporting)
3. [PDF Report Generation](#pdf-report-generation)
4. [QR Code Generation](#qr-code-generation)
5. [Database Schema](#database-schema)

---

## 🗣️ Feedback System

Inspector feedback system for quality tracking and AI model improvement.

### POST /api/feedback

Create new inspector feedback for an inspection.

**Request Body:**
```json
{
  "inspection_id": 1,
  "feedback_type": "Correct prediction",
  "comments": "Optional detailed comments"
}
```

**Feedback Types:**
- `"Correct prediction"` - AI was correct
- `"False positive"` - AI incorrectly flagged a defect
- `"Missed defect"` - AI missed an actual defect
- `"Needs manual review"` - Uncertain, needs human verification

**Response (201):**
```json
{
  "id": 1,
  "inspection_id": 1,
  "feedback_type": "Correct prediction",
  "comments": "Optional detailed comments",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/feedback" \
  -H "Content-Type: application/json" \
  -d '{"inspection_id": 1, "feedback_type": "Correct prediction", "comments": "Great detection!"}'
```

### GET /api/feedback

Retrieve all feedback records.

**Response (200):**
```json
[
  {
    "id": 1,
    "inspection_id": 1,
    "feedback_type": "Correct prediction",
    "comments": "Great detection!",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

## 📊 Analytics & Reporting

Quality analytics and trend analysis.

### GET /api/analytics/summary

Get overall inspection statistics.

**Response (200):**
```json
{
  "total_inspections": 150,
  "pass_count": 120,
  "review_count": 20,
  "reject_count": 10,
  "defect_rate": 6.67
}
```

**Defect Rate Calculation:**
```
Defect Rate = (reject_count / total_inspections) × 100
```

**cURL Example:**
```bash
curl "http://localhost:8000/api/analytics/summary"
```

### GET /api/analytics/trends

Get daily inspection trends.

**Response (200):**
```json
{
  "trends": [
    {
      "date": "2024-01-15",
      "total": 25,
      "pass_count": 20,
      "review_count": 3,
      "reject_count": 2
    },
    {
      "date": "2024-01-14",
      "total": 30,
      "pass_count": 25,
      "review_count": 4,
      "reject_count": 1
    }
  ]
}
```

**cURL Example:**
```bash
curl "http://localhost:8000/api/analytics/trends"
```

---

## 📄 PDF Report Generation

Generate professional PDF inspection reports.

### GET /api/inspections/{inspection_id}/report

Generate and download PDF report for an inspection.

**Parameters:**
- `inspection_id` (path) - Inspection ID

**Response (200):**
- Content-Type: `application/pdf`
- Downloads PDF file containing:
  - Inspection details (ID, product ID, status, score, timestamp)
  - Original product image
  - Defect heatmap visualization
  - Decision summary

**cURL Example:**
```bash
curl "http://localhost:8000/api/inspections/1/report" \
  -o inspection_report_1.pdf
```

**Browser Usage:**
```
http://localhost:8000/api/inspections/1/report
```

**Report Contents:**
- ✅ Inspection metadata table
- 🖼️ Original product image (4"×3")
- 🔥 Heatmap visualization (4"×3")
- 📝 Status interpretation

---

## 🔲 QR Code Generation

Digital defect passport via QR codes.

### GET /api/inspections/{inspection_id}/qr

Generate QR code linking to inspection details.

**Parameters:**
- `inspection_id` (path) - Inspection ID

**Response (200):**
- Content-Type: `image/png`
- High-resolution QR code image

**QR Code Links To:**
```
http://localhost:3000/inspections/{inspection_id}
```

**cURL Example:**
```bash
curl "http://localhost:8000/api/inspections/1/qr" \
  -o inspection_qr_1.png
```

**Browser Usage:**
```
http://localhost:8000/api/inspections/1/qr
```

**QR Code Specs:**
- Error Correction: High (H level)
- Box Size: 10 pixels
- Border: 4 boxes
- Colors: Black on white

---

## 🗄️ Database Schema

### Feedback Table

```sql
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    inspection_id INTEGER NOT NULL REFERENCES inspections(id) ON DELETE CASCADE,
    feedback_type VARCHAR(100) NOT NULL,
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_feedback_inspection (inspection_id),
    INDEX idx_feedback_type_created (feedback_type, created_at)
);
```

**Columns:**
- `id` - Primary key
- `inspection_id` - Foreign key to inspections table
- `feedback_type` - Type of feedback (see Feedback System section)
- `comments` - Optional detailed comments (max 2000 chars)
- `created_at` - Timestamp of feedback submission

---

## 🚀 Quick Start

### 1. Start the Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

### 2. Access Swagger UI

Open browser to: http://localhost:8000/docs

### 3. Test New Endpoints

Run the comprehensive test script:

```powershell
cd backend
python test_new_features.py
```

---

## 📁 File Structure

New files added:

```
backend/
├── app/
│   ├── models/
│   │   └── feedback.py           # Feedback ORM model
│   ├── schemas/
│   │   ├── feedback.py           # Feedback Pydantic schemas
│   │   └── analytics.py          # Analytics Pydantic schemas
│   ├── repositories/
│   │   ├── feedback.py           # Feedback data access layer
│   │   └── analytics.py          # Analytics data access layer
│   ├── services/
│   │   ├── feedback.py           # Feedback business logic
│   │   ├── analytics.py          # Analytics business logic
│   │   ├── pdf_report.py         # PDF generation service
│   │   └── qr_code.py            # QR code generation service
│   └── routers/
│       ├── feedback.py           # Feedback API endpoints
│       ├── analytics.py          # Analytics API endpoints
│       └── reports.py            # Report & QR endpoints
├── uploads/
│   ├── reports/                  # Generated PDF reports
│   └── qrs/                      # Generated QR codes
└── test_new_features.py          # Comprehensive test script
```

---

## ✅ Feature Checklist

- [x] Feedback system (POST & GET)
- [x] Analytics summary endpoint
- [x] Analytics trends endpoint
- [x] PDF report generation
- [x] QR code generation
- [x] Database migrations (Feedback table)
- [x] Complete test coverage
- [x] API documentation

---

## 🔗 Related Endpoints

Existing endpoints that work with new features:

- `POST /inspect` - Create inspection (generates ID for feedback/reports)
- `GET /inspections` - List all inspections
- `GET /inspections/{id}` - Get specific inspection details
- `GET /health` - Health check

---

## 📝 Notes

- All endpoints use standard REST conventions
- Error responses include descriptive messages
- CORS enabled for frontend integration
- Foreign key constraints ensure data integrity
- Static file serving for generated reports and QR codes

---

## 🐛 Troubleshooting

### Issue: "Inspection not found"
**Solution:** Ensure the inspection_id exists. Check with `GET /inspections`

### Issue: "Module not found: reportlab"
**Solution:** Install dependencies: `pip install reportlab qrcode[pil]`

### Issue: PDF images not showing
**Solution:** Verify image paths exist and are accessible

### Issue: QR code not scanning
**Solution:** Check base_url configuration in QRCodeService

---

For more information, visit the Swagger UI at http://localhost:8000/docs
