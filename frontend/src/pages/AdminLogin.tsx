import { useState, type FormEvent } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';
import Header from '../components/Header';
import { setAdminToken } from '../adminAuth';

export default function AdminLogin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    axios.post('http://localhost:8000/api/admin/login', { email, password })
      .then((response) => {
        setAdminToken(response.data.access_token);
        navigate('/admin');
      })
      .catch(() => setError('Invalid email or password.'))
      .finally(() => setIsSubmitting(false));
  };

  return (
    <div className="h-screen flex flex-col">
      <Header label="Admin" />
      <div className="flex-1 flex items-center justify-center">
        <div className="w-[400px] flex flex-col gap-5">
          <div className="text-center mb-1">
            <div
              className="w-[52px] h-[52px] rounded-xl flex items-center justify-center mx-auto mb-4"
              style={{ background: 'oklch(0.27 0.06 250)' }}
            >
              <ShieldCheck size={26} color="#fff" />
            </div>
            <h1 className="text-[21px] font-bold mb-1 font-serif">Sign in to CivicTriage Admin</h1>
            <div className="text-[13.5px] text-slate-500">Administrator access</div>
          </div>

          <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-[10px] p-[26px] flex flex-col gap-4 shadow-sm">
            <label className="flex flex-col gap-1.5 text-[12.5px] font-semibold text-slate-600">
              Email
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
        </div>
      </div>
    </div>
  );
}
