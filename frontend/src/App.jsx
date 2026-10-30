import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import Dashboard from './pages/Dashboard';
import NewInspection from './pages/NewInspection';
import InspectionResults from './pages/InspectionResults';
import InspectionHistory from './pages/InspectionHistory';
import SystemInfo from './pages/SystemInfo';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="inspect" element={<NewInspection />} />
          <Route path="results/:id" element={<InspectionResults />} />
          <Route path="history" element={<InspectionHistory />} />
          <Route path="system" element={<SystemInfo />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
