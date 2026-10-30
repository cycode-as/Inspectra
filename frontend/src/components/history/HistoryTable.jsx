import { useNavigate } from 'react-router-dom';
import { 
  ArrowUpRight, 
  Image as ImageIcon, 
  FileQuestion
} from 'lucide-react';
import { 
  normalizeStatus, 
  formatScore, 
  formatInferenceTime, 
  formatDateTime 
} from '../../utils/formatters';
import { resolveImageUrl } from '../../services/api';
import './history.css';

export default function HistoryTable({ inspections = [], loading = false }) {
  const navigate = useNavigate();

  const handleRowClick = (item) => {
    navigate(`/results/${item.id}`, { state: { inspection: item } });
  };

  if (loading) {
    return (
      <div className="card" style={{ padding: 'var(--space-12)', textAlign: 'center' }}>
        <div className="spinner spinner-lg" style={{ margin: '0 auto var(--space-4)' }}></div>
        <h3>Loading Inspection Records...</h3>
        <p>Syncing log entries from database.</p>
      </div>
    );
  }

  if (inspections.length === 0) {
    return (
      <div className="card empty-state-box">
        <FileQuestion size={40} className="text-secondary" style={{ opacity: 0.5 }} />
        <h4>No Matching Inspection Records</h4>
        <p>No records match your query or filters. Clear your filters or run a new inspection.</p>
      </div>
    );
  }

  return (
    <div className="table-container history-table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            <th style={{ width: '80px' }}>Thumbnail</th>
            <th>Inspection ID</th>
            <th>Product ID</th>
            <th>Status</th>
            <th>Anomaly Score</th>
            <th>Inference Time</th>
            <th>Timestamp</th>
            <th style={{ textAlign: 'right' }}>Action</th>
          </tr>
        </thead>
        <tbody>
          {inspections.map((item) => {
            const status = normalizeStatus(item.status);
            const statusClass = 
              status === 'PASS' ? 'status-pass' :
              status === 'REJECT' ? 'status-reject' :
              status === 'REVIEW' ? 'status-review' : 'status-neutral';

            const thumbSrc = resolveImageUrl(item.original_image || item.heatmap_image);

            return (
              <tr 
                key={item.id} 
                onClick={() => handleRowClick(item)}
                className="interactive-row"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    handleRowClick(item);
                  }
                }}
              >
                {/* Thumbnail Column */}
                <td>
                  <div className="table-thumb-box">
                    {thumbSrc ? (
                      <img 
                        src={thumbSrc} 
                        alt={item.product_id || 'Specimen'} 
                        className="table-thumb-img"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    ) : (
                      <ImageIcon size={16} className="text-muted" />
                    )}
                  </div>
                </td>

                {/* Inspection ID */}
                <td className="font-mono">
                  <span className="record-id-chip">#{item.id || 'N/A'}</span>
                </td>

                {/* Product ID */}
                <td>
                  <span className="product-id-text font-mono">
                    {item.product_id || '—'}
                  </span>
                </td>

                {/* Status Badge */}
                <td>
                  <span className={`status-badge ${statusClass}`}>
                    <span className="status-dot"></span>
                    {status}
                  </span>
                </td>

                {/* Anomaly Score */}
                <td className="font-mono">
                  <span className="score-text">
                    {formatScore(item.anomaly_score)}
                  </span>
                </td>

                {/* Inference Time */}
                <td className="font-mono text-secondary">
                  {formatInferenceTime(item.inference_time_ms)}
                </td>

                {/* Timestamp */}
                <td className="font-mono text-secondary" style={{ fontSize: 'var(--font-size-xs)' }}>
                  {formatDateTime(item.created_at)}
                </td>

                {/* Action Link */}
                <td style={{ textAlign: 'right' }}>
                  <button 
                    type="button" 
                    className="btn btn-secondary btn-sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRowClick(item);
                    }}
                  >
                    <span>View Result</span>
                    <ArrowUpRight size={13} />
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
