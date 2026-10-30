import { useState } from 'react';
import { 
  Columns, 
  Layers, 
  AlertCircle, 
  Image as ImageIcon
} from 'lucide-react';
import { resolveImageUrl } from '../../services/api';
import './heatmap.css';

export default function HeatmapViewer({ 
  originalImage, 
  heatmapImage, 
  productId
}) {
  const [viewMode, setViewMode] = useState('side-by-side'); // 'side-by-side' | 'overlay'
  const [overlayOpacity, setOverlayOpacity] = useState(0.65);

  const fullOriginalUrl = resolveImageUrl(originalImage);
  const fullHeatmapUrl = resolveImageUrl(heatmapImage);

  return (
    <div className="card heatmap-viewer-card">
      <div className="card-header heatmap-header">
        <div className="heatmap-header-left">
          <span className="card-title">
            <Layers size={18} className="text-secondary" />
            <span>Optical & Anomaly Heatmap Comparative Analysis</span>
          </span>
          <span className="tech-tag">PATCHCORE EMBEDDINGS</span>
        </div>

        {/* View Mode Switcher */}
        <div className="viewer-controls">
          <div className="btn-group">
            <button
              type="button"
              className={`btn btn-sm ${viewMode === 'side-by-side' ? 'btn-steel' : 'btn-secondary'}`}
              onClick={() => setViewMode('side-by-side')}
              title="Compare side by side"
            >
              <Columns size={13} />
              <span>Side-by-Side</span>
            </button>
            <button
              type="button"
              className={`btn btn-sm ${viewMode === 'overlay' ? 'btn-steel' : 'btn-secondary'}`}
              onClick={() => setViewMode('overlay')}
              title="Superimpose heatmap over original specimen"
            >
              <Layers size={13} />
              <span>Alpha Overlay</span>
            </button>
          </div>

          {viewMode === 'overlay' && (
            <div className="opacity-slider-wrap font-mono">
              <span className="slider-label">HEAT BLEND: {Math.round(overlayOpacity * 100)}%</span>
              <input
                type="range"
                min="0.1"
                max="1"
                step="0.05"
                value={overlayOpacity}
                onChange={(e) => setOverlayOpacity(parseFloat(e.target.value))}
                className="opacity-slider"
              />
            </div>
          )}
        </div>
      </div>

      <div className="card-body heatmap-body">
        {viewMode === 'side-by-side' ? (
          <div className="comparison-grid">
            {/* Panel 1: Original Specimen Image */}
            <div className="image-panel">
              <div className="image-panel-header">
                <span className="panel-badge font-mono">RAW OPTICAL CAPTURE</span>
                <span className="panel-meta font-mono">Channel: RGB 24-bit</span>
              </div>
              <div className="image-display-frame">
                {fullOriginalUrl ? (
                  <img
                    src={fullOriginalUrl}
                    alt={`Original capture of ${productId || 'specimen'}`}
                    className="specimen-img"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                ) : null}
                {!fullOriginalUrl && (
                  <div className="image-placeholder">
                    <ImageIcon size={32} />
                    <span>Original image unavailable</span>
                  </div>
                )}
                <div className="frame-crosshair-tag font-mono">SPECIMEN REF: 01</div>
              </div>
            </div>

            {/* Panel 2: AI Anomaly Heatmap */}
            <div className="image-panel">
              <div className="image-panel-header">
                <span className="panel-badge panel-badge-ai font-mono">
                  PATCHCORE ANOMALY HEATMAP
                </span>
                <span className="panel-meta font-mono">Feature Distance</span>
              </div>
              <div className="image-display-frame">
                {fullHeatmapUrl ? (
                  <img
                    src={fullHeatmapUrl}
                    alt={`AI Heatmap for ${productId || 'specimen'}`}
                    className="specimen-img heatmap-img"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                ) : null}
                {!fullHeatmapUrl && (
                  <div className="image-placeholder">
                    <AlertCircle size={32} />
                    <span>Heatmap not generated or unavailable</span>
                  </div>
                )}
                <div className="frame-crosshair-tag font-mono">HEAT MAP SEGMENTATION</div>
              </div>
            </div>
          </div>
        ) : (
          /* Overlay Mode */
          <div className="overlay-view-wrapper">
            <div className="overlay-frame">
              {fullOriginalUrl && (
                <img
                  src={fullOriginalUrl}
                  alt="Original base"
                  className="overlay-base-img"
                />
              )}
              {fullHeatmapUrl && (
                <img
                  src={fullHeatmapUrl}
                  alt="Heatmap overlay"
                  className="overlay-layer-img"
                  style={{ opacity: overlayOpacity }}
                />
              )}
              <div className="overlay-badge font-mono">
                COMPOSITE: {Math.round(overlayOpacity * 100)}% HEATMAP BLEND
              </div>
            </div>
          </div>
        )}

        {/* Heatmap Colormap Scale Legend */}
        <div className="heatmap-legend">
          <div className="legend-label font-mono">ANOMALY DENSITY GRADIENT:</div>
          <div className="legend-bar-wrapper">
            <span className="legend-tag-low font-mono">0.0 (Nominal Surface)</span>
            <div className="legend-gradient-bar"></div>
            <span className="legend-tag-high font-mono">1.0 (Critical Defect Peak)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
