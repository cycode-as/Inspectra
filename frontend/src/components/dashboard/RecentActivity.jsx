import { Link } from 'react-router-dom';
import { ArrowUpRight, FileQuestion, Image as ImageIcon } from 'lucide-react';
import { normalizeStatus, formatScore, formatInferenceTime, formatDateTime } from '../../utils/formatters';
import { resolveImageUrl } from '../../services/api';

export default function RecentActivity({ inspections = [], loading = false }) {
  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <span className="card-title">Recent Inspection Stream</span>
        </div>
        <div className="card-body" style={{ textAlign: 'center', padding: 'var(--space-8)' }}>
          <div className="spinner spinner-lg" style={{ margin: '0 auto var(--space-3)' }}></div>
          <p>Syncing inspection stream from server...</p>
        </div>
      </div>
    );
  }

  const recentItems = inspections.slice(0, 6);

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <span className="card-title">Recent Inspection Stream</span>
          <p className="card-subtitle">Last {recentItems.length} parts evaluated by PatchCore model</p>
        </div>
        <Link to="/history" className="btn btn-ghost btn-sm">
          <span>View All Log ({inspections.length})</span>
          <ArrowUpRight size={14} />
        </Link>
      </div>

      <div className="card-body" style={{ padding: 0 }}>
        {recentItems.length === 0 ? (
          <div className="empty-state-box">
            <FileQuestion size={36} className="text-secondary" style={{ opacity: 0.5 }} />
            <h4>No Inspections Recorded Yet</h4>
            <p>Upload a metal nut image to execute the first anomaly detection inference.</p>
            <Link to="/inspect" className="btn btn-primary btn-sm" style={{ marginTop: 'var(--space-3)' }}>
              Start Inspection
            </Link>
          </div>
        ) : (
          <div className="activity-list">
            {recentItems.map((item) => {
              const status = normalizeStatus(item.status);
              const statusClass = 
                status === 'PASS' ? 'status-pass' :
                status === 'REJECT' ? 'status-reject' :
                status === 'REVIEW' ? 'status-review' : 'status-neutral';

              const thumbnailSrc = resolveImageUrl(item.original_image || item.heatmap_image);

              return (
                <div key={item.id} className="activity-item">
                  <div className="activity-thumb-wrapper">
                    {thumbnailSrc ? (
                      <img 
                        src={thumbnailSrc} 
                        alt={item.product_id || 'Inspection sample'} 
                        className="activity-thumb"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    <div 
                      className="activity-thumb-fallback" 
                      style={{ display: thumbnailSrc ? 'none' : 'flex' }}
                    >
                      <ImageIcon size={16} />
                    </div>
                  </div>

                  <div className="activity-info">
                    <div className="activity-top-row">
                      <span className="activity-product font-mono">{item.product_id || `ID #${item.id}`}</span>
                      <span className={`status-badge ${statusClass}`}>
                        <span className="status-dot"></span>
                        {status}
                      </span>
                    </div>

                    <div className="activity-meta-row font-mono">
                      <span>Score: <strong>{formatScore(item.anomaly_score)}</strong></span>
                      <span className="meta-sep">•</span>
                      <span>{formatInferenceTime(item.inference_time_ms)}</span>
                      <span className="meta-sep">•</span>
                      <span>{formatDateTime(item.created_at)}</span>
                    </div>
                  </div>

                  <Link 
                    to={`/results/${item.id}`} 
                    state={{ inspection: item }}
                    className="btn btn-secondary btn-sm activity-action-btn"
                  >
                    <span>Inspect</span>
                    <ArrowUpRight size={13} />
                  </Link>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
