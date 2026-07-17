import { useState, type FormEvent } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Landmark } from 'lucide-react';
import Header from '../components/Header';
import { setTenantToken } from '../tenantAuth';

export default function TenantLogin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    axios.post('http://localhost:8000/api/tenant/login', { email, password })
      .then((response) => {
        setTenantToken(response.data.access_token);
        navigate('/');
      })
      .catch(() => setError('Invalid email or password.'))
      .finally(() => setIsSubmitting(false));
  };

  return (
    <div className="h-screen flex flex-col">
      <Header />
      <div className="flex-1 flex items-center justify-center">
        <div className="w-[400px] flex flex-col gap-5">
          <div className="text-center mb-1">
            <div
              className="w-[52px] h-[52px] rounded-xl flex items-center justify-center mx-auto mb-4"
              style={{ background: 'oklch(0.27 0.06 250)' }}
            >
              <Landmark size={26} color="#fff" />
            </div>
            <h1 className="text-[21px] font-bold mb-1 font-serif">Sign in to CivicTriage</h1>
            <div className="text-[13.5px] text-slate-500">Staff Portal</div>
          </div>

          <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-[10px] p-[26px] flex flex-col gap-4 shadow-sm">
            <label className="flex flex-col gap-1.5 text-[12.5px] font-semibold text-slate-600">
              Work email
              <input
                type="email"
                required
                className="border border-slate-300 rounded-md px-3 py-2.5 text-sm font-normal"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </label>

            <label className="flex flex-col gap-1.5 text-[12.5px] font-semibold text-slate-600">
              Password
              <input
                type="password"
                required
                className="border border-slate-300 rounded-md px-3 py-2.5 text-sm font-normal"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </label>

            {error && <p className="text-sm text-red-600">{error}</p>}

            <button
              type="submit"
              disabled={isSubmitting}
              className="text-white rounded-md py-2.5 text-sm font-bold mt-1 disabled:opacity-60"
              style={{ background: 'oklch(0.27 0.06 250)' }}
            >
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <div className="text-center text-xs text-slate-500">
            Having trouble signing in? Contact your system administrator.
          </div>
        </div>
      </div>
    </div>
  );
}
