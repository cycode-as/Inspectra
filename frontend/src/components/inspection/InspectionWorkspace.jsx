import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Play, 
  RotateCcw, 
  ShieldAlert, 
  Loader2
} from 'lucide-react';
import ImageUpload from './ImageUpload';
import ImagePreview from './ImagePreview';
import { submitInspection } from '../../services/api';
import './inspection.css';

export default function InspectionWorkspace() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [productId, setProductId] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionStep, setSubmissionStep] = useState(0);
  const [apiError, setApiError] = useState(null);
  const hiddenInputRef = useRef(null);

  // Manage object URL lifecycle
  const handleFileSelect = (file) => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setApiError(null);
  };

  const handleRemove = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
    setApiError(null);
  };

  const handleReplace = () => {
    if (hiddenInputRef.current) {
      hiddenInputRef.current.click();
    }
  };

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  // Stepped progress during inference
  useEffect(() => {
    if (!isSubmitting) return;

    const timer = setInterval(() => {
      setSubmissionStep((prev) => (prev < 3 ? prev + 1 : prev));
    }, 700);

    return () => clearInterval(timer);
  }, [isSubmitting]);

  const handleRunInspection = async () => {
    if (!selectedFile) return;

    setIsSubmitting(true);
    setSubmissionStep(1);
    setApiError(null);

    try {
      const result = await submitInspection(selectedFile, productId);
      // Navigate to results screen with inspection state and id
      const targetId = result.id || 'current';
      navigate(`/results/${targetId}`, { state: { inspection: result } });
    } catch (err) {
      setApiError(err.message || 'Inspection failed. Please verify backend service.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="inspection-workspace">
      {/* Hidden file input for replace action */}
      <input
        ref={hiddenInputRef}
        type="file"
        accept=".png,.jpg,.jpeg,image/png,image/jpeg"
        onChange={(e) => {
          if (e.target.files && e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
          }
        }}
        style={{ display: 'none' }}
      />

      {/* Main Staging & Upload Area */}
      {!selectedFile ? (
        <ImageUpload 
          onImageSelect={handleFileSelect} 
          disabled={isSubmitting} 
        />
      ) : (
        <ImagePreview
          file={selectedFile}
          previewUrl={previewUrl}
          productId={productId}
          onProductIdChange={setProductId}
          onRemove={handleRemove}
          onReplace={handleReplace}
          disabled={isSubmitting}
        />
      )}

      {/* API Error Notification */}
      {apiError && (
        <div className="alert-banner alert-danger">
          <ShieldAlert size={18} style={{ flexShrink: 0, marginTop: 2 }} />
          <div>
            <strong>Inspection Error:</strong> {apiError}
          </div>
        </div>
      )}

      {/* Bottom Action Command Bar */}
      {selectedFile && (
        <div className="inspection-action-bar card">
          <div className="action-bar-left">
            <div className="action-summary font-mono">
              <span>SPECIMEN: <strong>{selectedFile.name}</strong></span>
              <span className="summary-sep">|</span>
              <span>ENGINE: <strong>PatchCore</strong></span>
            </div>
          </div>

          <div className="action-bar-right">
            <button
              type="button"
              onClick={handleRemove}
              disabled={isSubmitting}
              className="btn btn-secondary"
            >
              <RotateCcw size={15} />
              <span>Cancel</span>
            </button>

            <button
              type="button"
              onClick={handleRunInspection}
              disabled={isSubmitting}
              className="btn btn-primary btn-lg run-inspection-btn"
            >
              {isSubmitting ? (
                <>
                  <Loader2 size={18} className="spinner" />
                  <span>
                    {submissionStep === 1 && 'Uploading Specimen...'}
                    {submissionStep === 2 && 'Extracting Features (PatchCore)...'}
                    {submissionStep === 3 && 'Evaluating Anomaly Heatmap...'}
                    {submissionStep === 0 && 'Executing Inference...'}
                  </span>
                </>
              ) : (
                <>
                  <Play size={18} fill="currentColor" />
                  <span>Run PatchCore Inspection</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
