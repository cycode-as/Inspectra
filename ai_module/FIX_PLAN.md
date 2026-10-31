# INSPECTRA - Critical Issues Fix Plan

## 🔴 Critical Issues Identified

### Issue 1: Background Sensitivity & Domain Shift
**Problem:** PatchCore trained on dark/textured backgrounds fails on bright/white backgrounds or hand-held objects
**Root Cause:** Feature extractor captures background features, not just object features
**Impact:** Wrong anomaly scores, false rejections

### Issue 2: Anomaly Score Saturation
**Problem:** Scores saturate at 1.0 for out-of-distribution samples
**Root Cause:** Static normalization bounds don't adapt to domain shifts
**Impact:** All novel samples get max score → automatic rejection

### Issue 3: Async Heatmap File Writing Race Condition
**Problem:** HTTP response returns before heatmap file is fully written
**Root Cause:** visualize_anomaly_map saves asynchronously without confirmation
**Impact:** 404/403 errors, frontend can't load heatmaps

### Issue 4: Image Normalization Pipeline Failure
**Problem:** Raw 0-255 RGB arrays passed to model without normalization
**Root Cause:** Missing pixel scaling (/255) and ImageNet mean/std normalization
**Impact:** Saturated activations, constant maximum anomaly distances

---

## ✅ Fix Strategy

### Fix 1: Background-Agnostic Feature Extraction
**Approach:** Implement object-focused preprocessing with background neutralization
**Techniques:**
1. Background subtraction using GrabCut/adaptive thresholding
2. Focus mask on anomaly map to weight object regions
3. Optional: Domain adaptation layer for background invariance

### Fix 2: Adaptive Anomaly Score Normalization
**Approach:** Dynamic calibration with percentile-based bounds
**Techniques:**
1. Track running statistics of anomaly distances
2. Use percentile-based normalization (e.g., 95th percentile as max)
3. Implement smooth score mapping with configurable thresholds

### Fix 3: Synchronous Heatmap File Writing
**Approach:** Ensure file is fully written before returning
**Techniques:**
1. Add explicit file flush and sync
2. Verify file existence and readability before returning path
3. Add retry logic with exponential backoff

### Fix 4: Correct Image Normalization Pipeline
**Approach:** Implement proper ImageNet normalization
**Techniques:**
1. Scale pixels to [0, 1] range (/255.0)
2. Apply channel-wise mean/std normalization
3. Verify tensor shapes and value ranges

---

## 📁 Files to Modify

1. `ai_module/predict.py` - Main prediction logic
2. `ai_module/preprocessing.py` - NEW: Preprocessing utilities
3. `ai_module/normalization.py` - NEW: Score normalization
4. `backend/app/services/inference.py` - Validation & error handling

---

## 🚀 Implementation Steps

1. Create preprocessing module with background removal
2. Create normalization module with adaptive calibration
3. Update predict.py with fixes for all 4 issues
4. Add comprehensive testing
5. Update documentation

---

Generated: 2024
Status: READY FOR IMPLEMENTATION
