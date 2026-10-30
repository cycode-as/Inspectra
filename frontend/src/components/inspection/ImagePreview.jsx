import { useState, useEffect } from 'react';
import { 
  Trash2, 
  RefreshCw 
} from 'lucide-react';
import { formatFileSize } from '../../utils/formatters';

export default function ImagePreview({ 
  file, 
  previewUrl, 
  onRemove, 
  onReplace, 
  productId, 
  onProductIdChange,
  disabled = false 
}) {
  const [dimensions, setDimensions] = useState({ width: null, height: null });

  useEffect(() => {
    if (!previewUrl) return;
    const img = new Image();
    img.src = previewUrl;
    img.onload = () => {
      setDimensions({ width: img.naturalWidth, height: img.naturalHeight });
    };
  }, [previewUrl]);

  return (
    <div className="preview-container card">
      <div className="card-header">
        <div className="preview-header-title">
          <span className="card-title">Staged Specimen Preview</span>
          <span className="tech-tag">READY FOR INFERENCE</span>
        </div>
        <div className="preview-header-actions">
          <button 
            type="button" 
            onClick={onReplace} 
            disabled={disabled}
            className="btn btn-secondary btn-sm"
            title="Replace specimen image"
          >
            <RefreshCw size={13} />
            <span>Replace</span>
          </button>
          <button 
            type="button" 
            onClick={onRemove} 
            disabled={disabled}
            className="btn btn-outline-danger btn-sm"
            title="Clear and remove image"
          >
            <Trash2 size={13} />
            <span>Remove</span>
          </button>
        </div>
      </div>

      <div className="preview-body">
        {/* Optical Frame */}
        <div className="optical-frame">
          <div className="optical-reticle">
            <span className="reticle-h"></span>
            <span className="reticle-v"></span>
          </div>
          <img 
            src={previewUrl} 
            alt={file?.name || 'Metal nut specimen'} 
            className="staged-image" 
          />
          <div className="optical-calibration-tag font-mono">
            CALIBRATED: METAL NUT
          </div>
        </div>

        {/* Specimen Telemetry & Optional Product Identifier */}
        <div className="preview-metadata-panel">
          <div className="input-group">
            <label className="input-label" htmlFor="productIdInput">
              Product Serial / Part ID (Optional)
            </label>
            <input
              id="productIdInput"
              type="text"
              className="input-field font-mono"
              placeholder="e.g. INS-001 or NUT-M12-09"
              value={productId}
              onChange={(e) => onProductIdChange(e.target.value)}
              disabled={disabled}
            />
            <span className="input-hint">
              If omitted, backend will assign the sequential station identifier.
            </span>
          </div>

          <div className="metadata-spec-list">
            <div className="spec-meta-item">
              <span className="spec-meta-label">File Name</span>
              <span className="spec-meta-val font-mono" title={file?.name}>
                {file?.name || 'specimen.png'}
              </span>
            </div>

            <div className="spec-meta-item">
              <span className="spec-meta-label">File Size</span>
              <span className="spec-meta-val font-mono">
                {formatFileSize(file?.size)}
              </span>
            </div>

            <div className="spec-meta-item">
              <span className="spec-meta-label">Resolution</span>
              <span className="spec-meta-val font-mono">
                {dimensions.width && dimensions.height
                  ? `${dimensions.width} × ${dimensions.height} px`
                  : 'Measuring...'}
              </span>
            </div>

            <div className="spec-meta-item">
              <span className="spec-meta-label">Encoding</span>
              <span className="spec-meta-val font-mono">
                {file?.type || 'image/png'}
              </span>
            </div>

            <div className="spec-meta-item">
              <span className="spec-meta-label">Target Model</span>
              <span className="spec-meta-val">PatchCore AI</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
