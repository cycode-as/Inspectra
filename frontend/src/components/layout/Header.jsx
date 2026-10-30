import { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { 
  Menu, 
  Plus, 
  Wifi, 
  WifiOff, 
  RefreshCw, 
  Clock
} from 'lucide-react';
import { checkSystemHealth, API_BASE_URL } from '../../services/api';
import './layout.css';

export default function Header({ onMenuClick }) {
  const location = useLocation();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [connectionStatus, setConnectionStatus] = useState({
    checking: true,
    isOnline: false,
    latencyMs: 0
  });

  // Keep digital clock updating every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Check backend connection on mount & poll every 30s
  const checkHealth = async () => {
    setConnectionStatus((prev) => ({ ...prev, checking: true }));
    const result = await checkSystemHealth();
    setConnectionStatus({
      checking: false,
      isOnline: result.isOnline,
      latencyMs: result.latencyMs || 0
    });
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Derive page heading based on current path
  const getPageInfo = () => {
    switch (location.pathname) {
      case '/':
        return {
          title: 'Quality Overview Dashboard',
          section: 'SYSTEM METRICS'
        };
      case '/inspect':
        return {
          title: 'New Inspection Workstation',
          section: 'MANUFACTURING QA'
        };
      case '/history':
        return {
          title: 'Inspection Records Log',
          section: 'AUDIT & COMPLIANCE'
        };
      case '/system':
        return {
          title: 'System & Engine Specification',
          section: 'DIAGNOSTICS'
        };
      default:
        if (location.pathname.startsWith('/results/')) {
          return {
            title: 'Inspection Results & Heatmap Analysis',
            section: 'INFERENCE REPORT'
          };
        }
        return {
          title: 'Inspection Station',
          section: 'INSPECTRA'
        };
    }
  };

  const pageInfo = getPageInfo();

  const formattedDate = currentTime.toLocaleDateString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: '2-digit'
  });

  const formattedTime = currentTime.toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });

  return (
    <header className="app-header">
      <div className="header-left">
        <button 
          className="header-menu-btn" 
          onClick={onMenuClick}
          aria-label="Toggle navigation menu"
        >
          <Menu size={20} />
        </button>

        <div className="header-breadcrumbs">
          <span className="breadcrumb-section">{pageInfo.section}</span>
          <span className="breadcrumb-sep">/</span>
          <h1 className="header-title">{pageInfo.title}</h1>
        </div>
      </div>

      <div className="header-right">
        {/* Real-time Industrial Timestamp */}
        <div className="header-time-block font-mono">
          <Clock size={14} className="time-icon" />
          <span>{formattedDate}</span>
          <span className="time-divider">|</span>
          <span className="time-val">{formattedTime}</span>
        </div>

        {/* Backend Connection Badge */}
        <div 
          className={`conn-badge ${connectionStatus.isOnline ? 'conn-online' : 'conn-offline'}`}
          title={`Backend Server: ${API_BASE_URL}`}
          onClick={checkHealth}
          role="button"
          tabIndex={0}
        >
          {connectionStatus.checking ? (
            <RefreshCw size={13} className="spinner" />
          ) : connectionStatus.isOnline ? (
            <Wifi size={13} />
          ) : (
            <WifiOff size={13} />
          )}
          <span className="conn-text">
            {connectionStatus.checking
              ? 'PINGING...'
              : connectionStatus.isOnline
              ? `API ONLINE (${connectionStatus.latencyMs}ms)`
              : 'API OFFLINE'}
          </span>
        </div>

        {/* Quick New Inspection Button */}
        {location.pathname !== '/inspect' && (
          <Link to="/inspect" className="btn btn-primary btn-sm header-action-btn">
            <Plus size={15} />
            <span>New Inspection</span>
          </Link>
        )}
      </div>
    </header>
  );
}
