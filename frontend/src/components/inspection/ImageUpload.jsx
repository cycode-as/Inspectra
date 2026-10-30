import { useState, useRef } from 'react';
import { UploadCloud, AlertCircle, Crosshair } from 'lucide-react';
import './inspection.css';

const ACCEPTED_TYPES = ['image/png', 'image/jpeg', 'image/jpg'];
const ACCEPTED_EXTENSIONS = ['.png', '.jpg', '.jpeg'];

export default function ImageUpload({ onImageSelect, disabled = false }) {
  const [isDragging, setIsDragging] = useState(false);
  const [validationError, setValidationError] = useState('');
  const fileInputRef = useRef(null);

  const validateAndProcessFile = (file) => {
    setValidationError('');
    if (!file) return;

    // Check MIME type or filename extension
    const hasValidType = ACCEPTED_TYPES.includes(file.type);
    const hasValidExt = ACCEPTED_EXTENSIONS.some((ext) =>
      file.name.toLowerCase().endsWith(ext)
    );

    if (!hasValidType && !hasValidExt) {
      setValidationError('Unsupported format. Please provide a PNG, JPG, or JPEG image file.');
      return;
    }

    // Check reasonable file size (e.g. max 20MB)
    if (file.size > 20 * 1024 * 1024) {
      setValidationError('Image size exceeds 20 MB limit. Please select a lighter image.');
      return;
    }

    onImageSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      validateAndProcessFile(droppedFile);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndProcessFile(e.target.files[0]);
    }
  };

  const handleBrowseClick = () => {
    if (fileInputRef.current && !disabled) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="upload-wrapper">
      <input
        ref={fileInputRef}
        type="file"
        accept=".png,.jpg,.jpeg,image/png,image/jpeg"
        onChange={handleFileChange}
        style={{ display: 'none' }}
        disabled={disabled}
      />

      <div
        className={`industrial-dropzone ${isDragging ? 'dropzone-active' : ''} ${
          disabled ? 'dropzone-disabled' : ''
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleBrowseClick}
        role="button"
        tabIndex={disabled ? -1 : 0}
        onKeyDown={(e) => {
          if ((e.key === 'Enter' || e.key === ' ') && !disabled) {
            handleBrowseClick();
          }
        }}
      >
        {/* Technical Corner Brackets */}
        <div className="corner-bracket corner-tl"></div>
        <div className="corner-bracket corner-tr"></div>
        <div className="corner-bracket corner-bl"></div>
        <div className="corner-bracket corner-br"></div>

        {/* Reticle / Optical Target Overlay */}
        <div className="viewfinder-grid">
          <div className="viewfinder-crosshair">
            <Crosshair size={28} className="crosshair-icon" />
          </div>
        </div>

        <div className="dropzone-content">
          <div className="dropzone-icon-bubble">
            <UploadCloud size={32} />
          </div>

          <h3 className="dropzone-title">
            Mount Metal Nut Specimen Image
          </h3>

          <p className="dropzone-instructions">
            Drag & drop raw specimen capture here, or <span className="browse-link">browse workstation disk</span>
          </p>

          <div className="specimen-tags">
            <span className="tech-tag">PNG</span>
            <span className="tech-tag">JPG</span>
            <span className="tech-tag">JPEG</span>
            <span className="tech-tag">Target: Metal Nut</span>
          </div>

          <div className="dropzone-hint">
            Recommended: Minimum 256×256 px resolution with diffuse lighting for optimal PatchCore feature alignment.
          </div>
        </div>
      </div>

      {validationError && (
        <div className="alert-banner alert-danger" style={{ marginTop: 'var(--space-3)' }}>
          <AlertCircle size={16} style={{ flexShrink: 0, marginTop: 2 }} />
          <span>{validationError}</span>
        </div>
      )}
    </div>
  );
}
