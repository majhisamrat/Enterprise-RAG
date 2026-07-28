import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/axios';
import { useAuthStore } from '../store/authStore';

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const setToken = useAuthStore((s) => s.setToken);
  const navigate = useNavigate();

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const { data } = await api.post('/auth/login', { email, password });
      setToken(data.access_token);
      navigate('/');
    } catch {
      setError('Sign in failed. Check your credentials or use local development mode.');
    }
  };

  return (
    <div className="login">
      <form className="login-card" onSubmit={submit}>
        <div className="app-brand">
          <span>◇</span> enterprise rag
        </div>
        <h1>Welcome back.</h1>
        <p>Sign in to your organization workspace.</p>
        <label className="field">
          Email
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="user@enterprise.com"
          />
        </label>
        <label className="field">
          Password
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
          />
        </label>
        {error && <div className="error">{error}</div>}
        <button className="button" type="submit">
          Sign in
        </button>
        <small>For development, the FastAPI API supports unauthenticated local requests.</small>
      </form>
    </div>
  );
}
