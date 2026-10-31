# 🔄 Migration Guide: Switching to Fixed Predict Function

## Overview

This guide explains how to migrate from `predict.py` to `predict_fixed.py` without breaking existing functionality.

---

## 🎯 Migration Strategy

### Option 1: Gradual Rollout (Recommended)

Keep both versions running and gradually switch endpoints:

```python
# backend/app/routers/inspections.py

# Import both versions
from ai_module.predict import predict as predict_original
from ai_module.predict_fixed import predict as predict_fixed
import os

# Use environment variable to control which version
USE_FIXED_PREDICT = os.getenv("USE_FIXED_PREDICT", "false").lower() == "true"

@router.post("/inspect")
async def create_inspection(...):
    # Choose predict function based on environment variable
    predict_func = predict_fixed if USE_FIXED_PREDICT else predict_original
    
    # Call the chosen function
    result = predict_func(image_path)
    ...
```

Enable the fixed version:

```powershell
# Set environment variable
$env:USE_FIXED_PREDICT = "true"

# Or in .env file
echo "USE_FIXED_PREDICT=true" >> backend/.env
```

### Option 2: Direct Replacement

Replace the import directly:

```python
# backend/app/routers/inspections.py

# OLD:
# from ai_module.predict import predict

# NEW:
from ai_module.predict_fixed import predict
```

### Option 3: Rename Files (Clean Cutover)

1. Backup original:
```powershell
cd ai_module
cp predict.py predict_original_backup.py
```

2. Replace original with fixed version:
```powershell
cp predict_fixed.py predict.py
```

3. No code changes needed in backend!

---

## 🔧 Configuration for Fixed Version

### Environment Variables

Create `ai_module/.env`:

```ini
# Background removal settings
USE_BACKGROUND_REMOVAL=true
BACKGROUND_METHOD=grabcut  # grabcut, threshold, edge, none

# Score normalization settings
USE_ADAPTIVE_NORMALIZATION=true
PERCENTILE_MAX=95.0
PERCENTILE_MIN=5.0

# Heatmap settings
HEATMAP_MAX_RETRIES=3
HEATMAP_RETRY_DELAY=0.1

# Status thresholds
PASS_THRESHOLD=0.35
REVIEW_THRESHOLD=0.65
```

### Load Configuration

Update `predict_fixed.py` to read environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration from environment
USE_BG_REMOVAL = os.getenv("USE_BACKGROUND_REMOVAL", "true").lower() == "true"
BG_METHOD = os.getenv("BACKGROUND_METHOD", "grabcut")
USE_ADAPTIVE_NORM = os.getenv("USE_ADAPTIVE_NORMALIZATION", "true").lower() == "true"
```

---

## 🧪 Testing Migration

### Step 1: Test Fixed Version Independently

```powershell
cd ai_module

# Test with a known image
python predict_fixed.py datasets/metal_nut/test/bent/000.png

# Compare with original
python predict.py datasets/metal_nut/test/bent/000.png
```

### Step 2: Run Comprehensive Tests

```powershell
python test_all_fixes.py datasets/metal_nut/test/bent/000.png
```

Expected output:
```
✅ PASSED: Background Removal
✅ PASSED: Adaptive Normalization
✅ PASSED: Heatmap Sync
✅ PASSED: Score Ranges

Overall: 4/4 tests passed
```

### Step 3: Test Backend Integration

```powershell
cd backend
.\venv\Scripts\Activate.ps1

# Set to use fixed version
$env:USE_FIXED_PREDICT = "true"

# Start server
uvicorn main:app --reload

# In another terminal, test API
curl -X POST "http://localhost:8000/inspect" \
  -F "file=@test_image.jpg" \
  -F "product_id=TEST-001"
```

### Step 4: Compare Results

Create a comparison script:

```python
# compare_predictions.py
from ai_module.predict import predict as predict_old
from ai_module.predict_fixed import predict as predict_new

image_path = "test_image.jpg"

result_old = predict_old(image_path)
result_new = predict_new(image_path)

print("ORIGINAL:")
print(f"  Score: {result_old['anomaly_score']:.4f}")
print(f"  Status: {result_old['status']}")

print("\nFIXED:")
print(f"  Score: {result_new['anomaly_score']:.4f} (raw: {result_new['raw_score']:.4f})")
print(f"  Status: {result_new['status']}")
print(f"  Bounds: {result_new['normalization_bounds']}")
```

---

## 📊 Expected Differences

### Score Differences

The fixed version may produce different scores due to:

1. **Background removal:** Focuses on object, ignoring background
2. **Adaptive normalization:** Adjusts bounds based on recent predictions

**Example:**

| Image | Original Score | Fixed Score | Reason |
|-------|---------------|-------------|--------|
| White background | 0.95 (REJECT) | 0.45 (REVIEW) | Background removed |
| Normal sample | 0.52 (REVIEW) | 0.48 (PASS) | Better normalization |
| Severe defect | 0.98 (REJECT) | 0.85 (REJECT) | Prevented saturation |

### Status Changes

Status decisions may change due to new thresholds:

| Score Range | Old Status | New Status | Change |
|-------------|-----------|-----------|--------|
| 0.35-0.45 | PASS | PASS | Same |
| 0.45-0.55 | REVIEW | PASS | More lenient |
| 0.55-0.65 | REJECT | REVIEW | More lenient |
| 0.65+ | REJECT | REJECT | Same |

---

## 🚨 Rollback Plan

### If Issues Occur

1. **Immediate Rollback (Environment Variable):**
```powershell
$env:USE_FIXED_PREDICT = "false"
# Restart backend
```

2. **Rollback Import:**
```python
# backend/app/routers/inspections.py
from ai_module.predict import predict  # Original version
```

3. **Delete Fixed Version:**
```powershell
cd ai_module
rm predict_fixed.py preprocessing.py normalization.py
```

### Preserve Data

Score statistics are saved to:
```
ai_module/results/score_stats.json
```

Backup before migration:
```powershell
cp ai_module/results/score_stats.json ai_module/results/score_stats.backup.json
```

---

## ✅ Migration Checklist

- [ ] Backup original `predict.py`
- [ ] Deploy new files (`preprocessing.py`, `normalization.py`, `predict_fixed.py`)
- [ ] Run `test_all_fixes.py` successfully
- [ ] Test on representative dataset
- [ ] Configure environment variables
- [ ] Update backend imports
- [ ] Test backend integration
- [ ] Monitor score statistics file creation
- [ ] Verify no 404 errors on heatmaps
- [ ] Compare prediction results
- [ ] Document any status threshold adjustments
- [ ] Prepare rollback plan
- [ ] Monitor performance metrics
- [ ] Gradual rollout to production

---

## 📈 Monitoring After Migration

### Key Metrics to Watch

1. **Score Distribution:**
```powershell
# Check if scores are well-distributed
cat ai_module/results/score_stats.json
```

2. **Heatmap Success Rate:**
```
Monitor backend logs for "Heatmap saved and verified" messages
```

3. **Inference Time:**
```
Background removal adds 20-500ms depending on method
```

4. **Status Distribution:**
```
Track PASS/REVIEW/REJECT ratios before and after migration
```

### Alert on Issues

- Scores all saturating at 1.0 → Adaptive normalization not working
- 404 errors on heatmaps → File sync issue
- Inference time > 2 seconds → Background removal too slow
- All predictions REJECT → Threshold misconfiguration

---

## 🎓 Training for Operators

### Key Changes to Communicate

1. **Background Independence:**
   - System now works on any background
   - Hand-held objects are supported
   - Place object anywhere in frame

2. **Improved Calibration:**
   - Scores adapt over time
   - First 20-30 predictions may have wider ranges
   - System learns normal vs anomalous distribution

3. **More Lenient Thresholds:**
   - REVIEW zone widened (0.35-0.65 instead of 0.45-0.55)
   - Fewer false rejections
   - More samples flagged for human review

4. **No More 404 Errors:**
   - Heatmaps guaranteed to be available
   - Synchronous file operations

---

## 📝 Documentation Updates

Update user-facing documentation:

1. **API Documentation:**
   - Note background independence
   - Explain adaptive scoring
   - Update example responses

2. **Operator Manual:**
   - New status thresholds
   - Background handling
   - Score interpretation

3. **Technical Docs:**
   - Architecture updates
   - Configuration options
   - Troubleshooting guide

---

**Migration Timeline:** Allow 1-2 weeks for gradual rollout  
**Rollback Window:** Keep original version for 30 days  
**Success Criteria:** <1% error rate, improved accuracy on bright backgrounds

---

Need help? Review `IMPLEMENTATION_GUIDE.md` or check test output.
