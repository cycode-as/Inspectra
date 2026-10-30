import { Search, X } from 'lucide-react';
import './history.css';

export default function HistoryFilters({
  searchTerm,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  sortBy,
  onSortChange,
  totalResults,
  onReset
}) {
  const statuses = ['ALL', 'PASS', 'REJECT', 'REVIEW'];

  const hasActiveFilters = searchTerm.trim() !== '' || statusFilter !== 'ALL' || sortBy !== 'newest';

  return (
    <div className="card history-filters-card">
      <div className="filters-row">
        {/* Search Input */}
        <div className="search-input-wrapper">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            className="input-field search-field font-mono"
            placeholder="Search by Product ID or Record #..."
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
          />
          {searchTerm && (
            <button
              type="button"
              className="search-clear-btn"
              onClick={() => onSearchChange('')}
              aria-label="Clear search"
            >
              <X size={14} />
            </button>
          )}
        </div>

        {/* Status Filter Segmented Controls */}
        <div className="status-filter-group">
          <span className="filter-group-label">STATUS:</span>
          <div className="btn-group">
            {statuses.map((st) => (
              <button
                key={st}
                type="button"
                className={`btn btn-sm ${statusFilter === st ? 'btn-steel' : 'btn-secondary'}`}
                onClick={() => onStatusFilterChange(st)}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        {/* Sort Dropdown */}
        <div className="sort-filter-group">
          <span className="filter-group-label">SORT:</span>
          <select
            className="input-field sort-select"
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value)}
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="score_desc">Anomaly Score (Highest)</option>
            <option value="score_asc">Anomaly Score (Lowest)</option>
          </select>
        </div>

        {/* Reset Filters */}
        {hasActiveFilters && (
          <button
            type="button"
            className="btn btn-ghost btn-sm reset-btn"
            onClick={onReset}
          >
            <X size={13} />
            <span>Reset</span>
          </button>
        )}
      </div>

      <div className="filters-meta-row font-mono">
        <span>SHOWING {totalResults} INSPECTION RECORDS</span>
      </div>
    </div>
  );
}
