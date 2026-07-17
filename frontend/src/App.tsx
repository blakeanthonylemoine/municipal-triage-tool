import type { ReactNode } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import TicketQueue from './components/TicketQueue';
import TenantLogin from './pages/TenantLogin';
import AdminLogin from './pages/AdminLogin';
import AdminDashboard from './pages/AdminDashboard';
import { isAdminAuthenticated } from './adminAuth';
import { isTenantAuthenticated } from './tenantAuth';

function RequireAdmin({ children }: { children: ReactNode }) {
  if (!isAdminAuthenticated()) {
    return <Navigate to="/admin/login" replace />;
  }
  return <>{children}</>;
}

function RequireTenant({ children }: { children: ReactNode }) {
  if (!isTenantAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<TenantLogin />} />
      <Route
        path="/"
        element={
          <RequireTenant>
            <div className="min-h-screen bg-slate-100">
              <header className="bg-white border-b border-slate-200 px-6 py-4">
                <h1 className="text-xl font-bold text-slate-900">Municipal Triage Tool</h1>
              </header>
              <TicketQueue />
            </div>
          </RequireTenant>
        }
      />
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route
        path="/admin"
        element={
          <RequireAdmin>
            <AdminDashboard />
          </RequireAdmin>
        }
      />
    </Routes>
  );
}
