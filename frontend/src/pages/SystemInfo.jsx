import { useState, useEffect } from 'react';
import { 
  Cpu, 
  Server, 
  RefreshCw, 
  ShieldCheck
} from 'lucide-react';
import { checkSystemHealth, API_BASE_URL, UPLOAD_FIELD_NAME } from '../services/api';

export default function SystemInfo() {
  const [health, setHealth] = useState({ checking: true, isOnline: false, latencyMs: 0 });

  const runHealthCheck = async () => {
    setHealth({ checking: true, isOnline: false, latencyMs: 0 });
    const res = await checkSystemHealth();
    setHealth({ checking: false, isOnline: res.isOnline, latencyMs: res.latencyMs || 0 });
  };

  useEffect(() => {
    runHealthCheck();
  }, []);

  return (
    <div className="system-page" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Header Bar */}
      <div className="station-header-bar">
        <div>
          <div className="station-breadcrumb font-mono">
            <span>DIAGNOSTICS</span>
            <span className="breadcrumb-dot">/</span>
            <span>SYSTEM SPECIFICATION</span>
          </div>
          <h2 className="station-heading">System & Engine Architecture</h2>
          <p className="station-subheading">
            Technical configuration for INSPECTRA Edge Workstation & FastAPI Inference Service.
          </p>
        </div>

        <button 
          onClick={runHealthCheck} 
          className="btn btn-secondary"
          disabled={health.checking}
        >
          <RefreshCw size={14} className={health.checking ? 'spinner' : ''} />
          <span>Ping Service</span>
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-6)' }}>
        {/* Card 1: Backend Connection Status */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">
              <Server size={18} className="text-secondary" />
              <span>Backend Service Status</span>
            </span>
            <span className={`status-badge ${health.isOnline ? 'status-pass' : 'status-reject'}`}>
              <span className="status-dot"></span>
              {health.checking ? 'PROBING' : health.isOnline ? 'ONLINE' : 'OFFLINE'}
            </span>
          </div>
          <div className="card-body">
            <div className="system-specs-list">
              <div className="spec-row">
                <span className="spec-name">API Base Endpoint</span>
                <span className="spec-data font-mono">{API_BASE_URL}</span>
              </div>
              <div className="spec-row">
                <span className="spec-name">Upload Field Name</span>
                <span className="spec-data font-mono">{UPLOAD_FIELD_NAME}</span>
              </div>
              <div className="spec-row">
                <span className="spec-name">Roundtrip Latency</span>
                <span className="spec-data font-mono">
                  {health.checking ? 'Measuring...' : health.isOnline ? `${health.latencyMs} ms` : 'N/A'}
                </span>
              </div>
              <div className="spec-row">
                <span className="spec-name">Framework Protocol</span>
                <span className="spec-data">FastAPI REST / HTTP 1.1</span>
              </div>
              <div className="spec-row">
                <span className="spec-name">Database Target</span>
                <span className="spec-data font-mono">PostgreSQL</span>
              </div>
            </div>
          </div>
        </div>

        {/* Card 2: AI Engine Architecture */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">
              <Cpu size={18} className="text-secondary" />
              <span>Anomaly Detection Engine</span>
            </span>
            <span className="status-badge status-neutral">PATCHCORE</span>
          </div>
          <div className="card-body">
            <div className="system-specs-list">
              <div className="spec-row">
                <span className="spec-name">Model Name</span>
                <span className="spec-data">PatchCore</span>
              </div>
              <div className="spec-row">
                <span className="spec-name">Backbone Feature Extractor</span>
                <span className="spec-data font-mono">ResNet-50 (Pretrained)</span>
              </div>
              <div className="spec-row">
                <span className="spec-name">Memory Bank Reduction</span>
                <span className="spec-data font-mono">Coreset Subsampling (10%)</span>
              </div>
              <div className="spec-row">
                <span className="spec-name">Neighborhood Aggregation</span>
                <span className="spec-data font-mono">Greedy Coreset Matching</span>
              </div>
              <div className="spec-row">
                <span className="spec-name">Output Artifacts</span>
                <span className="spec-data">Anomaly Score & Heatmap Matrix</span>
              </div>
            </div>
          </div>
        </div>

        {/* Card 3: Quality Inspection Specimen Profile */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">
              <ShieldCheck size={18} className="text-secondary" />
              <span>Inspection Specimen Parameters</span>
            </span>
          </div>
          <div className="card-body">
            <div className="system-specs-list">
              <div className="spec-row">
                <span className="spec-name">Product Category</span>
                <span className="spec-data font-semibold">Manufactured Metal Nut</span>
              </div>
              <div className="spec-row">
                <span className="spec-name">Valid Image Formats</span>
                <span className="spec-data font-mono">PNG, JPG, JPEG</span>
              </div>
              <div className="spec-row">
                <span className="spec-name">Target Anomaly Classes</span>
                <span className="spec-data">Thread Burrs, Scratches, Oxidation</span>
              </div>
              <div className="spec-row">
                <span className="spec-name">Decision Classes</span>
                <span className="spec-data font-mono">PASS, REJECT, REVIEW</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
