import { 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Layers, 
  Gauge
} from 'lucide-react';
import { normalizeStatus } from '../../utils/formatters';

export default function StatOverview({ inspections = [] }) {
  const total = inspections.length;
  
  let passCount = 0;
  let rejectCount = 0;
  let reviewCount = 0;
  let totalInferenceMs = 0;
  let inferenceCount = 0;

  inspections.forEach((item) => {
    const status = normalizeStatus(item.status);
    if (status === 'PASS') passCount++;
    else if (status === 'REJECT') rejectCount++;
    else if (status === 'REVIEW') reviewCount++;

    if (item.inference_time_ms && !isNaN(Number(item.inference_time_ms))) {
      totalInferenceMs += Number(item.inference_time_ms);
      inferenceCount++;
    }
  });

  const passRate = total > 0 ? ((passCount / total) * 100).toFixed(1) + '%' : '—';
  const avgInference = inferenceCount > 0 ? Math.round(totalInferenceMs / inferenceCount) + ' ms' : '—';

  return (
    <div className="stats-grid">
      {/* Total Inspections */}
      <div className="stat-card stat-total">
        <div className="stat-label">
          <span>Total Inspections</span>
          <Layers size={16} className="text-secondary" />
        </div>
        <div className="stat-value">{total}</div>
        <div className="stat-meta font-mono">
          <span>Recorded in system</span>
        </div>
      </div>

      {/* Passed Products */}
      <div className="stat-card stat-pass">
        <div className="stat-label">
          <span>Passed (Nominal)</span>
          <CheckCircle2 size={16} style={{ color: 'var(--status-pass-fg)' }} />
        </div>
        <div className="stat-value" style={{ color: 'var(--status-pass-fg)' }}>
          {passCount}
        </div>
        <div className="stat-meta">
          <span className="font-mono">{passRate}</span>
          <span>pass yield</span>
        </div>
      </div>

      {/* Rejected Products */}
      <div className="stat-card stat-reject">
        <div className="stat-label">
          <span>Rejected (Defective)</span>
          <XCircle size={16} style={{ color: 'var(--status-reject-fg)' }} />
        </div>
        <div className="stat-value" style={{ color: 'var(--status-reject-fg)' }}>
          {rejectCount}
        </div>
        <div className="stat-meta">
          <span className="font-mono">
            {total > 0 ? ((rejectCount / total) * 100).toFixed(1) + '%' : '—'}
          </span>
          <span>defect rate</span>
        </div>
      </div>

      {/* Needs Review */}
      <div className="stat-card stat-review">
        <div className="stat-label">
          <span>Requires Review</span>
          <AlertTriangle size={16} style={{ color: 'var(--status-review-fg)' }} />
        </div>
        <div className="stat-value" style={{ color: 'var(--status-review-fg)' }}>
          {reviewCount}
        </div>
        <div className="stat-meta">
          <span className="font-mono">
            {total > 0 ? ((reviewCount / total) * 100).toFixed(1) + '%' : '—'}
          </span>
          <span>borderline cases</span>
        </div>
      </div>

      {/* Avg Inference Latency */}
      <div className="stat-card">
        <div className="stat-label">
          <span>Avg Inference Time</span>
          <Gauge size={16} className="text-secondary" />
        </div>
        <div className="stat-value font-mono">
          {avgInference}
        </div>
        <div className="stat-meta">
          <span>PatchCore model speed</span>
        </div>
      </div>
    </div>
  );
}
