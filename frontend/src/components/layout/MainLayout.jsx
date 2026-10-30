import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';

export default function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-shell">
      <Sidebar 
        isOpen={sidebarOpen} 
        onClose={() => setSidebarOpen(false)} 
      />
      <div className="main-wrapper">
        <Header 
          onMenuClick={() => setSidebarOpen((prev) => !prev)} 
        />
        <main className="page-container">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
