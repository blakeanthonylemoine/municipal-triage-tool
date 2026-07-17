import { useEffect, useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { KeyRound, LogOut, Plus } from 'lucide-react';
import Header from '../components/Header';
import adminApi from '../adminApi';
import { clearAdminToken } from '../adminAuth';
import type { TenantSummary } from '../types';

const NAVY = 'oklch(0.27 0.06 250)';

function CreateTenantForm({ onCreated }: { onCreated: () => void }) {
  const [name, setName] = useState('');
  const [loginEmail, setLoginEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    adminApi.post('/api/admin/tenants', { name, login_email: loginEmail, password })
      .then(() => {
        setName('');
        setLoginEmail('');
        setPassword('');
        onCreated();
      })
      .catch((err) => setError(err.response?.data?.detail ?? 'Failed to create tenant.'))
      .finally(() => setIsSubmitting(false));
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-[10px] shadow-sm p-5 mb-6 flex flex-wrap gap-4 items-end">
      <label className="text-sm text-slate-700">
        Municipality Name
        <input
          required
          className="mt-1 border border-slate-300 rounded-md px-3 py-2 text-sm block"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </label>
      <label className="text-sm text-slate-700">
        Login Email
        <input
          type="email"
          required
          className="mt-1 border border-slate-300 rounded-md px-3 py-2 text-sm block"
          value={loginEmail}
          onChange={(e) => setLoginEmail(e.target.value)}
        />
      </label>
      <label className="text-sm text-slate-700">
        Initial Password
        <input
          type="password"
          required
          className="mt-1 border border-slate-300 rounded-md px-3 py-2 text-sm block"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </label>
      {error && <span className="text-sm text-red-600">{error}</span>}
      <button
        type="submit"
        disabled={isSubmitting}
        className="flex items-center gap-2 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-60"
        style={{ background: NAVY }}
      >
        <Plus size={16} /> Create Tenant
      </button>
    </form>
  );
}

function ResetCredentialsRow({ tenant, onDone }: { tenant: TenantSummary; onDone: () => void }) {
  const [loginEmail, setLoginEmail] = useState(tenant.login_email ?? '');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    adminApi.patch(`/api/admin/tenants/${tenant.id}/credentials`, {
      login_email: loginEmail || null,
      password: password || null,
    })
      .then(() => onDone())
      .catch((err) => setError(err.response?.data?.detail ?? 'Failed to update credentials.'))
      .finally(() => setIsSubmitting(false));
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-wrap gap-3 items-end bg-slate-50 border border-slate-200 rounded-md p-4 mt-2">
      <label className="text-xs text-slate-600">
        Login Email
        <input
          type="email"
          className="mt-1 border border-slate-300 rounded-md px-2 py-1.5 text-sm block"
          value={loginEmail}
          onChange={(e) => setLoginEmail(e.target.value)}
        />
      </label>
      <label className="text-xs text-slate-600">
        New Password
        <input
          type="password"
          placeholder="Leave blank to keep current"
          className="mt-1 border border-slate-300 rounded-md px-2 py-1.5 text-sm block"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </label>
      {error && <span className="text-xs text-red-600">{error}</span>}
      <button
        type="submit"
        disabled={isSubmitting}
        className="text-white px-3 py-1.5 rounded-md text-xs font-medium disabled:opacity-60"
        style={{ background: NAVY }}
      >
        Save
      </button>
    </form>
  );
}

export default function AdminDashboard() {
  const [tenants, setTenants] = useState<TenantSummary[]>([]);
  const [resettingId, setResettingId] = useState<number | null>(null);
  const navigate = useNavigate();

  const fetchTenants = () => {
    adminApi.get('/api/admin/tenants')
      .then((response) => setTenants(response.data))
      .catch((error) => console.error('Error fetching tenants:', error));
  };

  useEffect(() => {
    fetchTenants();
  }, []);

  const handleLogout = () => {
    clearAdminToken();
    navigate('/admin/login');
  };

  const totals = tenants.reduce(
    (acc, tenant) => ({
      pending: acc.pending + tenant.pending_count,
      tokens: acc.tokens + tenant.input_tokens + tenant.output_tokens,
    }),
    { pending: 0, tokens: 0 }
  );

  return (
    <div className="min-h-screen">
      <Header label="Admin">
        <button onClick={handleLogout} className="flex items-center gap-2 text-sm text-white/80 hover:text-white">
          <LogOut size={16} /> Log Out
        </button>
      </Header>

      <div className="max-w-6xl mx-auto p-6">
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-white border border-slate-200 rounded-[10px] p-5">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Tenants</p>
            <p className="text-2xl font-bold text-slate-900 mt-1">{tenants.length}</p>
          </div>
          <div className="bg-white border border-slate-200 rounded-[10px] p-5">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Pending Tickets</p>
            <p className="text-2xl font-bold text-slate-900 mt-1">{totals.pending}</p>
          </div>
          <div className="bg-white border border-slate-200 rounded-[10px] p-5">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Tokens Used</p>
            <p className="text-2xl font-bold mt-1" style={{ color: 'oklch(0.35 0.06 190)' }}>{totals.tokens.toLocaleString()}</p>
          </div>
        </div>

        <CreateTenantForm onCreated={fetchTenants} />

        <div className="bg-white border border-slate-200 rounded-[10px] shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-5 py-3">Municipality</th>
                <th className="px-5 py-3">Login Email</th>
                <th className="px-5 py-3">Tickets</th>
                <th className="px-5 py-3">Tokens</th>
                <th className="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {tenants.map((tenant) => (
                <tr key={tenant.id} className="border-b border-slate-100 last:border-0 align-top">
                  <td className="px-5 py-4 font-medium text-slate-900">{tenant.name}</td>
                  <td className="px-5 py-4 text-slate-600">{tenant.login_email ?? '—'}</td>
                  <td className="px-5 py-4 text-slate-600">{tenant.pending_count} pending / {tenant.ticket_count} total</td>
                  <td className="px-5 py-4 text-slate-600">{(tenant.input_tokens + tenant.output_tokens).toLocaleString()}</td>
                  <td className="px-5 py-4">
                    <button
                      onClick={() => setResettingId(resettingId === tenant.id ? null : tenant.id)}
                      className="flex items-center gap-1 text-xs font-medium"
                      style={{ color: NAVY }}
                    >
                      <KeyRound size={14} /> Reset Credentials
                    </button>
                    {resettingId === tenant.id && (
                      <ResetCredentialsRow
                        tenant={tenant}
                        onDone={() => {
                          setResettingId(null);
                          fetchTenants();
                        }}
                      />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {tenants.length === 0 && (
            <p className="p-8 text-center text-slate-500">No tenants yet. Create one above.</p>
          )}
        </div>
      </div>
    </div>
  );
}
