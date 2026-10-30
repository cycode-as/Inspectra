import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  ScanLine, 
  History, 
  Cpu, 
  ChevronRight,
  Disc3
} from 'lucide-react';
import './layout.css';

export default function Sidebar({ isOpen, onClose }) {
  const navItems = [
    {
      to: '/',
      label: 'Overview',
      icon: LayoutDashboard,
      description: 'System metrics & activity'
    },
    {
      to: '/inspect',
      label: 'New Inspection',
      icon: ScanLine,
      description: 'Run PatchCore inference'
    },
    {
      to: '/history',
      label: 'Inspection Records',
      icon: History,
      description: 'Audit log & past results'
    },
    {
      to: '/system',
      label: 'System Spec',
      icon: Cpu,
      description: 'Model & backend telemetry'
    }
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div 
          className="sidebar-backdrop" 
          onClick={onClose} 
          aria-hidden="true" 
        />
      )}

      <aside className={`app-sidebar ${isOpen ? 'sidebar-open' : ''}`}>
        {/* Brand Header */}
        <div className="sidebar-brand">
          <div className="brand-mark">
            <Disc3 className="brand-icon" size={24} />
          </div>
          <div className="brand-info">
            <div className="brand-name">
              INSPECTRA<span className="brand-dot">.</span>
            </div>
            <div className="brand-sub">AI Industrial QA</div>
          </div>
        </div>

        {/* Manufacturing Spec Tag */}
        <div className="sidebar-spec-badge">
          <div className="spec-label">ACTIVE PROFILE</div>
          <div className="spec-value">
            <span className="spec-dot"></span>
            METAL NUT (M8-M24)
          </div>
        </div>

        {/* Navigation Group */}
        <div className="sidebar-nav-section">
          <div className="nav-group-title">WORKSPACE</div>
          <nav className="sidebar-nav">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={onClose}
                  className={({ isActive }) =>
                    `nav-link ${isActive ? 'nav-link-active' : ''}`
                  }
                  end={item.to === '/'}
                >
                  <Icon className="nav-icon" size={18} />
                  <div className="nav-text-container">
                    <span className="nav-label">{item.label}</span>
                    <span className="nav-desc">{item.description}</span>
                  </div>
                  <ChevronRight className="nav-arrow" size={14} />
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Engine Metadata Footer */}
        <div className="sidebar-footer">
          <div className="engine-card">
            <div className="engine-header">
              <span className="engine-title">MODEL ENGINE</span>
              <span className="tech-tag">v2.4</span>
            </div>
            <div className="engine-name">PatchCore (Anomaly)</div>
            <div className="engine-meta font-mono">ResNet-50 Feature Extractor</div>
          </div>

          <div className="sidebar-status-row">
            <div className="status-indicator">
              <span className="status-dot-active"></span>
              <span>Station 01 Ready</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
