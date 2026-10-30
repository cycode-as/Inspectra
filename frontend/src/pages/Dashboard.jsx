import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ScanLine, 
  Cpu, 
  AlertCircle, 
  RefreshCw, 
  ArrowRight,
  FileCheck
} from 'lucide-react';
import StatOverview from '../components/dashboard/StatOverview';
import RecentActivity from '../components/dashboard/RecentActivity';
import { fetchInspections, checkSystemHealth, API_BASE_URL } from '../services/api';
import './dashboard.css';

export default function Dashboard() {
  const [inspections, setInspections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [systemHealth, setSystemHealth] = useState({ isOnline: false, latencyMs: 0 });

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [historyData, healthData] = await Promise.allSettled([
        fetchInspections(),
        checkSystemHealth()
      ]);

      if (historyData.status === 'fulfilled') {
        setInspections(historyData.value || []);
      } else {
        setError(historyData.reason?.message || 'Could not connect to inspection service.');
      }

      if (healthData.status === 'fulfilled') {
        setSystemHealth(healthData.value);
      }
    } catch (err) {
      setError(err.message || 'Error loading dashboard metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  return (
    <div className="dashboard-page">
      {/* Top Banner: Industrial Station Launchpad */}
      <section className="workstation-banner">
        <div className="banner-content">
          <div className="banner-badge">
            <span className="pulse-dot pulse-green"></span>
            <span>SYSTEM ACTIVE — STATION #01</span>
          </div>
          <h2 className="banner-title">Industrial Defect Detection & Quality Control</h2>
          <p className="banner-desc">
            Automated visual anomaly segmentation powered by <strong>PatchCore</strong> deep representation matching.
            Calibrated for manufactured metal nut surface integrity.
          </p>
        </div>

        <div className="banner-actions">
          <Link to="/inspect" className="btn btn-primary btn-lg banner-primary-btn">
            <ScanLine size={18} />
            <span>Launch New Inspection</span>
          </Link>
          <button 
            onClick={loadDashboardData} 
            className="btn btn-secondary banner-refresh-btn"
            title="Refresh dashboard data"
          >
            <RefreshCw size={16} className={loading ? 'spinner' : ''} />
            <span>Sync</span>
          </button>
        </div>
      </section>

      {/* Error Notice if API is down */}
      {error && (
        <div className="alert-banner alert-warning">
          <AlertCircle size={18} style={{ flexShrink: 0, marginTop: 2 }} />
          <div>
            <strong>Backend Connection Notice:</strong> {error}
            <div style={{ marginTop: 'var(--space-1)', fontSize: 'var(--font-size-xs)' }}>
              Server target: <code className="font-mono">{API_BASE_URL}</code>. If the backend is starting up or in development, click Sync once active.
            </div>
          </div>
        </div>
      )}

      {/* Section 1: Real System Statistics */}
      <section className="dashboard-section">
        <div className="section-header">
          <h3 className="section-title">Telemetry & Yield Statistics</h3>
          <span className="font-mono text-secondary" style={{ fontSize: 'var(--font-size-xs)' }}>
            Calculated from {inspections.length} recorded inspections
          </span>
        </div>
        <StatOverview inspections={inspections} />
      </section>

      {/* Section 2: Two-Column Layout (Recent Stream + Compact System Status) */}
      <div className="dashboard-grid">
        <div className="dashboard-main-col">
          <RecentActivity inspections={inspections} loading={loading} />
        </div>

        <aside className="dashboard-side-col">
          {/* Compact System Status Information */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">
                <Cpu size={16} className="text-secondary" />
                <span>Station Specification</span>
              </span>
              <span className={`status-badge ${systemHealth.isOnline ? 'status-pass' : 'status-review'}`}>
                {systemHealth.isOnline ? 'OPERATIONAL' : 'STANDBY'}
              </span>
            </div>

            <div className="card-body system-specs-list">
              <div className="spec-row">
                <span className="spec-name">Inference Model</span>
                <span className="spec-data font-mono">PatchCore (ResNet-50)</span>
              </div>
              <div className="spec-row">
                <span className="spec-name">Product Profile</span>
                <span className="spec-data">Metal Nut (Thread & Hex)</span>
              </div>
              <div className="spec-row">
                <span className="spec-name">Valid Image Types</span>
                <span className="spec-data font-mono">PNG, JPG, JPEG</span>
              </div>
              <div className="spec-row">
                <span className="spec-name">Backend Host</span>
                <span className="spec-data font-mono">{API_BASE_URL}</span>
              </div>
              <div className="spec-row">
                <span className="spec-name">Latency</span>
                <span className="spec-data font-mono">
                  {systemHealth.isOnline ? `${systemHealth.latencyMs} ms` : 'Offline'}
                </span>
              </div>
            </div>

            <div className="card-footer">
              <Link to="/system" className="btn btn-ghost btn-sm" style={{ width: '100%', justifyContent: 'space-between' }}>
                <span>View Full System Diagnostics</span>
                <ArrowRight size={14} />
              </Link>
            </div>
          </div>

          {/* Quick Quality Protocol Card */}
          <div className="card" style={{ marginTop: 'var(--space-4)' }}>
            <div className="card-header">
              <span className="card-title">
                <FileCheck size={16} className="text-secondary" />
                <span>Inspection Protocol</span>
              </span>
            </div>
            <div className="card-body protocol-body">
              <div className="protocol-step">
                <span className="protocol-number font-mono">01</span>
                <div>
                  <strong>Centering</strong>
                  <p>Center the metal nut evenly under uniform, diffuse lighting.</p>
                </div>
              </div>
              <div className="protocol-step">
                <span className="protocol-number font-mono">02</span>
                <div>
                  <strong>Resolution</strong>
                  <p>Capture at min 256x256 to ensure micro-crack visibility.</p>
                </div>
              </div>
              <div className="protocol-step">
                <span className="protocol-number font-mono">03</span>
                <div>
                  <strong>Scoring</strong>
                  <p>Heatmap peaks indicate structural anomaly distribution.</p>
                </div>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
