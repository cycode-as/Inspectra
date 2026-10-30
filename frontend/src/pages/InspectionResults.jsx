import { useState, useEffect } from 'react';
import { useParams, useLocation, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  RefreshCw, 
  AlertCircle, 
  ScanLine, 
  History,
  FileQuestion
} from 'lucide-react';
import HeatmapViewer from '../components/inspection/HeatmapViewer';
import ResultCard from '../components/inspection/ResultCard';
import { fetchInspectionById } from '../services/api';

export default function InspectionResults() {
  const { id } = useParams();
  const location = useLocation();

  // Check if inspection was passed via navigation state
  const stateInspection = location.state?.inspection;
  const [inspection, setInspection] = useState(stateInspection || null);
  const [loading, setLoading] = useState(!stateInspection && !!id && id !== 'current');
  const [error, setError] = useState(null);

  useEffect(() => {
    // If not in state and we have an ID other than 'current', fetch from API
    if (!stateInspection && id && id !== 'current') {
      let isMounted = true;
      setLoading(true);
      setError(null);

      fetchInspectionById(id)
        .then((record) => {
          if (isMounted) {
            setInspection(record);
            setLoading(false);
          }
        })
        .catch((err) => {
          if (isMounted) {
            setError(err.message || `Unable to load inspection record #${id}`);
            setLoading(false);
          }
        });

      return () => {
        isMounted = false;
      };
    }
  }, [id, stateInspection]);

  if (loading) {
    return (
      <div className="card" style={{ padding: 'var(--space-12)', textAlign: 'center' }}>
        <div className="spinner spinner-lg" style={{ margin: '0 auto var(--space-4)' }}></div>
        <h3>Retrieving Inspection Record #{id}...</h3>
        <p>Loading PatchCore inference embeddings and thermal anomaly matrix from database.</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card" style={{ padding: 'var(--space-8)' }}>
        <div className="alert-banner alert-danger">
          <AlertCircle size={20} style={{ flexShrink: 0, marginTop: 2 }} />
          <div>
            <strong>Unable to Retrieve Inspection:</strong> {error}
          </div>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-3)', marginTop: 'var(--space-4)' }}>
          <button 
            onClick={() => window.location.reload()} 
            className="btn btn-secondary"
          >
            <RefreshCw size={14} />
            <span>Retry Retrieval</span>
          </button>
          <Link to="/history" className="btn btn-secondary">
            <History size={14} />
            <span>Inspection Log</span>
          </Link>
          <Link to="/inspect" className="btn btn-primary">
            <ScanLine size={14} />
            <span>New Inspection</span>
          </Link>
        </div>
      </div>
    );
  }

  if (!inspection) {
    return (
      <div className="card" style={{ padding: 'var(--space-12)', textAlign: 'center' }}>
        <FileQuestion size={48} className="text-secondary" style={{ opacity: 0.5, margin: '0 auto var(--space-3)' }} />
        <h3>No Inspection Record Active</h3>
        <p>Please select an inspection record from the audit log or upload a new metal nut specimen.</p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--space-3)', marginTop: 'var(--space-5)' }}>
          <Link to="/inspect" className="btn btn-primary">
            <ScanLine size={16} />
            <span>Launch New Inspection</span>
          </Link>
          <Link to="/history" className="btn btn-secondary">
            <History size={16} />
            <span>View Inspection History</span>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="results-page" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Top Navigation Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
        <Link to="/history" className="btn btn-ghost btn-sm" style={{ paddingLeft: 0 }}>
          <ArrowLeft size={16} />
          <span>Back to Inspection Records</span>
        </Link>

        <div className="font-mono text-secondary" style={{ fontSize: 'var(--font-size-xs)' }}>
          RECORD IDENTIFIER: <strong>#{inspection.id || 'TEMP'}</strong> • PRODUCT: <strong>{inspection.product_id}</strong>
        </div>
      </div>

      {/* Screen 3 Core Feature 1: Significant visual prominence for Original and Heatmap */}
      <HeatmapViewer
        originalImage={inspection.original_image}
        heatmapImage={inspection.heatmap_image}
        productId={inspection.product_id}
        status={inspection.status}
      />

      {/* Screen 3 Core Feature 2: Result Card with exact anomaly score & decisions */}
      <ResultCard inspection={inspection} />
    </div>
  );
}
