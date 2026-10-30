# INSPECTRA — AI-Powered Industrial Defect Detection & QA System

Production-quality frontend for **INSPECTRA**, an industrial quality control inspection platform utilizing the **PatchCore** anomaly detection model for manufactured metal nuts.

## Architecture

```
frontend/
├── public/
│   ├── favicon.svg
│   └── icons.svg
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── MainLayout.jsx
│   │   │   └── layout.css
│   │   ├── dashboard/
│   │   │   ├── StatOverview.jsx
│   │   │   └── RecentActivity.jsx
│   │   ├── inspection/
│   │   │   ├── ImageUpload.jsx
│   │   │   ├── ImagePreview.jsx
│   │   │   ├── InspectionWorkspace.jsx
│   │   │   ├── ResultCard.jsx
│   │   │   ├── HeatmapViewer.jsx
│   │   │   ├── inspection.css
│   │   │   └── heatmap.css
│   │   └── history/
│   │       ├── HistoryTable.jsx
│   │       ├── HistoryFilters.jsx
│   │       └── history.css
│   │
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── NewInspection.jsx
│   │   ├── InspectionResults.jsx
│   │   ├── InspectionHistory.jsx
│   │   ├── SystemInfo.jsx
│   │   └── dashboard.css
│   │
│   ├── services/
│   │   └── api.js
│   │
│   ├── utils/
│   │   └── formatters.js
│   │
│   ├── styles/
│   │   ├── variables.css      # Central design tokens for effortless redesign
│   │   ├── global.css         # Typography, reset, and container primitives
│   │   └── components.css     # Modular industrial badges, cards, buttons, tables
│   │
│   ├── App.jsx                # React Router DOM configuration
│   ├── main.jsx
│   └── index.css
│
├── .env                       # VITE_API_BASE_URL=http://localhost:8000
└── package.json
```

## Running the Application

1. Enter the frontend directory:
   ```bash
   cd frontend
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open your browser at `http://localhost:5173`.

## Backend API Specification

Configure the backend endpoint in `frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

- **POST /inspect**: Accepts `multipart/form-data` with field `file` (and optional `product_id`). Returns `{ id, product_id, anomaly_score, status, original_image, heatmap_image, inference_time_ms }`.
- **GET /inspections**: Returns array of past inspections.
- **GET /inspections/{id}**: Returns inspection record by ID.
