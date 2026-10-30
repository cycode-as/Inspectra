import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { 
  ScanLine, 
  RefreshCw, 
  AlertCircle
} from 'lucide-react';
import HistoryFilters from '../components/history/HistoryFilters';
import HistoryTable from '../components/history/HistoryTable';
import { fetchInspections } from '../services/api';
import { normalizeStatus } from '../utils/formatters';

export default function InspectionHistory() {
  const [inspections, setInspections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters State
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('newest');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchInspections();
      setInspections(data);
    } catch (err) {
      setError(err.message || 'Failed to retrieve inspection records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Filter and sort records client-side
  const filteredInspections = useMemo(() => {
    let list = [...inspections];

    // Status filter
    if (statusFilter !== 'ALL') {
      list = list.filter((item) => normalizeStatus(item.status) === statusFilter);
    }

    // Search query filter
    if (searchTerm.trim()) {
      const q = searchTerm.trim().toLowerCase();
      list = list.filter((item) => {
        const idMatch = String(item.id || '').toLowerCase().includes(q);
        const prodMatch = String(item.product_id || '').toLowerCase().includes(q);
        return idMatch || prodMatch;
      });
    }

    // Sorting
    list.sort((a, b) => {
      if (sortBy === 'newest') {
        const dateA = new Date(a.created_at || 0).getTime();
        const dateB = new Date(b.created_at || 0).getTime();
        return dateB - dateA;
      }
      if (sortBy === 'oldest') {
        const dateA = new Date(a.created_at || 0).getTime();
        const dateB = new Date(b.created_at || 0).getTime();
        return dateA - dateB;
      }
      if (sortBy === 'score_desc') {
        return (Number(b.anomaly_score) || 0) - (Number(a.anomaly_score) || 0);
      }
      if (sortBy === 'score_asc') {
        return (Number(a.anomaly_score) || 0) - (Number(b.anomaly_score) || 0);
      }
      return 0;
    });

    return list;
  }, [inspections, statusFilter, searchTerm, sortBy]);

  const handleResetFilters = () => {
    setSearchTerm('');
    setStatusFilter('ALL');
    setSortBy('newest');
  };

  return (
    <div className="history-page">
      {/* Page Header */}
      <div className="station-header-bar">
        <div>
          <div className="station-breadcrumb font-mono">
            <span>AUDIT LOG</span>
            <span className="breadcrumb-dot">/</span>
            <span>QUALITY ARCHIVE</span>
          </div>
          <h2 className="station-heading">Inspection Records</h2>
          <p className="station-subheading">
            Historical PatchCore defect classifications, anomaly scores, and image records.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          <button 
            type="button" 
            onClick={loadData} 
            className="btn btn-secondary"
            title="Reload records from server"
          >
            <RefreshCw size={14} className={loading ? 'spinner' : ''} />
            <span>Sync</span>
          </button>

          <Link to="/inspect" className="btn btn-primary">
            <ScanLine size={16} />
            <span>New Inspection</span>
          </Link>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="alert-banner alert-danger">
          <AlertCircle size={18} style={{ flexShrink: 0, marginTop: 2 }} />
          <div>
            <strong>Service Connection Error:</strong> {error}
            <div style={{ marginTop: 'var(--space-2)' }}>
              <button onClick={loadData} className="btn btn-secondary btn-sm">
                Retry Connection
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Filter Toolbar */}
      <HistoryFilters
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
        sortBy={sortBy}
        onSortChange={setSortBy}
        totalResults={filteredInspections.length}
        onReset={handleResetFilters}
      />

      {/* Data Table */}
      <HistoryTable 
        inspections={filteredInspections} 
        loading={loading} 
      />
    </div>
  );
}
