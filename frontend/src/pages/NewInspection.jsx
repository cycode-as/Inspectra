import { 
  ShieldCheck, 
  Cpu, 
  CheckCircle2
} from 'lucide-react';
import InspectionWorkspace from '../components/inspection/InspectionWorkspace';
import './inspection.css';

export default function NewInspection() {
  return (
    <div className="new-inspection-page">
      {/* Station Header Bar */}
      <div className="station-header-bar">
        <div>
          <div className="station-breadcrumb font-mono">
            <span>STATION 01</span>
            <span className="breadcrumb-dot">/</span>
            <span>INSPECTION BENCH</span>
          </div>
          <h2 className="station-heading">Optical Defect Inspection</h2>
          <p className="station-subheading">
            Profile: <strong>Metal Nut (Thread & Hex Flange)</strong> • Model: <strong>PatchCore v2.4</strong>
          </p>
        </div>

        <div className="station-badges">
          <span className="tech-tag">
            <span className="status-dot-active" style={{ marginRight: 6 }}></span>
            PATCHCORE READY
          </span>
          <span className="tech-tag">M8 - M24 COMPATIBLE</span>
        </div>
      </div>

      {/* Main Inspection Workspace */}
      <InspectionWorkspace />

      {/* Bottom Technical Calibration Tips */}
      <div className="guidance-grid">
        <div className="guidance-card">
          <div className="guidance-header">
            <CheckCircle2 size={16} className="text-secondary" />
            <span>Optimal Specimen Alignment</span>
          </div>
          <p>
            Place the metal nut flat against the inspection bed with internal threading aligned perpendicular to the lens axis.
          </p>
        </div>

        <div className="guidance-card">
          <div className="guidance-header">
            <ShieldCheck size={16} className="text-secondary" />
            <span>Surface Anomaly Detection</span>
          </div>
          <p>
            PatchCore detects scratches, thread burrs, oxidation pits, foreign particle inclusion, and structural deformation.
          </p>
        </div>

        <div className="guidance-card">
          <div className="guidance-header">
            <Cpu size={16} className="text-secondary" />
            <span>Decision Thresholds</span>
          </div>
          <p>
            Anomaly score indicates memory-bank distance. Evaluated against certified tolerance bounds for PASS, REJECT, or REVIEW.
          </p>
        </div>
      </div>
    </div>
  );
}
