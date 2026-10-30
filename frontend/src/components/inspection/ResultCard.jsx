import { Link } from 'react-router-dom';
import { 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Gauge, 
  Tag, 
  Calendar,
  ScanLine,
  History,
  FileCheck2
} from 'lucide-react';
import { 
  normalizeStatus, 
  formatScore, 
  formatInferenceTime, 
  formatDateTime 
} from '../../utils/formatters';

export default function ResultCard({ inspection }) {
  if (!inspection) return null;

  const status = normalizeStatus(inspection.status);
  const statusClass = 
    status === 'PASS' ? 'status-pass' :
    status === 'REJECT' ? 'status-reject' :
    status === 'REVIEW' ? 'status-review' : 'status-neutral';

  const StatusIcon = 
    status === 'PASS' ? CheckCircle2 :
    status === 'REJECT' ? XCircle :
    status === 'REVIEW' ? AlertTriangle : FileCheck2;

  return (
    <div className={`card result-card ${statusClass}-border`}>
      {/* Top Banner Decision Strip */}
      <div className={`decision-banner ${statusClass}-banner`}>
        <div className="decision-left">
          <StatusIcon size={28} className="decision-icon" />
          <div>
            <div className="decision-title">QUALITY DECISION: {status}</div>
            <div className="decision-desc">
              {status === 'PASS' && 'Specimen surface integrity conforms to manufacturing baseline.'}
              {status === 'REJECT' && 'Anomalous surface feature pattern detected exceeding threshold.'}
              {status === 'REVIEW' && 'Marginal feature divergence requires manual QA inspector review.'}
              {status === 'UNKNOWN' && 'Classification state not provided by model server.'}
            </div>
          </div>
        </div>
        <div className="decision-badge-wrap">
          <span className={`status-badge status-badge-lg ${statusClass}`}>
            <span className="status-dot"></span>
            {status}
          </span>
        </div>
      </div>

      <div className="card-body result-details-body">
        {/* Metric Grid */}
        <div className="result-metric-grid">
          {/* Anomaly Score */}
          <div className="result-metric-box">
            <span className="result-metric-label">PatchCore Anomaly Score</span>
            <div className="result-metric-val font-mono">
              {formatScore(inspection.anomaly_score)}
            </div>
            <span className="result-metric-sub">
              Direct embedding distance score
            </span>
          </div>

          {/* Inference Time */}
          <div className="result-metric-box">
            <span className="result-metric-label">Model Inference Time</span>
            <div className="result-metric-val font-mono">
              {formatInferenceTime(inspection.inference_time_ms)}
            </div>
            <span className="result-metric-sub">
              Feature extraction & memory search
            </span>
          </div>

          {/* Product ID */}
          <div className="result-metric-box">
            <span className="result-metric-label">Product / Specimen ID</span>
            <div className="result-metric-val font-mono" style={{ fontSize: 'var(--font-size-xl)' }}>
              {inspection.product_id || '—'}
            </div>
            <span className="result-metric-sub">
              Target component identifier
            </span>
          </div>

          {/* Inspection Record ID */}
          <div className="result-metric-box">
            <span className="result-metric-label">Inspection Record ID</span>
            <div className="result-metric-val font-mono" style={{ fontSize: 'var(--font-size-xl)' }}>
              #{inspection.id || 'N/A'}
            </div>
            <span className="result-metric-sub">
              Database sequence index
            </span>
          </div>
        </div>

        {/* Technical Audit Metadata Row */}
        <div className="result-audit-meta">
          <div className="audit-col font-mono">
            <Calendar size={14} className="audit-icon" />
            <span>TIMESTAMP: {formatDateTime(inspection.created_at)}</span>
          </div>

          <div className="audit-col font-mono">
            <Tag size={14} className="audit-icon" />
            <span>PART CLASS: METAL NUT</span>
          </div>

          <div className="audit-col font-mono">
            <Gauge size={14} className="audit-icon" />
            <span>ENGINE: PATCHCORE (RESNET-50)</span>
          </div>
        </div>
      </div>

      {/* Navigation Actions Footer */}
      <div className="card-footer result-actions-footer">
        <div className="footer-left-actions">
          <Link to="/history" className="btn btn-secondary">
            <History size={16} />
            <span>Return to History Log</span>
          </Link>
        </div>

        <div className="footer-right-actions">
          <Link to="/inspect" className="btn btn-primary btn-lg">
            <ScanLine size={18} />
            <span>Inspect Next Specimen</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
