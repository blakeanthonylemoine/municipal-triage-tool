import { useState, type FormEvent } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
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
    <div className="min-h-screen bg-slate-100 flex items-center justify-center">
      <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-lg shadow-sm p-8 w-full max-w-sm">
        <h1 className="text-xl font-bold text-slate-900 mb-6">Admin Login</h1>

        <label className="block text-sm text-slate-700 mb-4">
          Email
          <input
            type="email"
            required
            className="mt-1 w-full border border-slate-300 rounded-md px-3 py-2 text-sm"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>

        <label className="block text-sm text-slate-700 mb-6">
          Password
          <input
            type="password"
            required
            className="mt-1 w-full border border-slate-300 rounded-md px-3 py-2 text-sm"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>

        {error && <p className="text-sm text-red-600 mb-4">{error}</p>}

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-60"
        >
          {isSubmitting ? 'Signing in...' : 'Sign In'}
        </button>
      </form>
    </div>
  );
}
