import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
import './AuthPage.css';

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!email || !password) {
      setError('Please fill in all fields.');
      return;
    }
    setLoading(true);
    // Simulate auth — replace with your real API call
    await new Promise(r => setTimeout(r, 1200));
    setLoading(false);
    navigate('/documents');
  };

  return (
    <div className="auth-page">
      <div className="auth-main">
        <div className="auth-card">
          <div className="auth-card__header">
            <h1 className="auth-card__title">Welcome back</h1>
            <p className="auth-card__sub">Access your legal workspace and documents securely.</p>
          </div>

          {error && <div className="auth-error">{error}</div>}

          <form className="auth-form" onSubmit={handleSubmit} noValidate>
            <div className="auth-field">
              <label className="auth-label" htmlFor="email">EMAIL ADDRESS</label>
              <input
                id="email"
                className="auth-input"
                type="email"
                placeholder="name@company.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>

            <div className="auth-field">
              <div className="auth-label-row">
                <label className="auth-label" htmlFor="password">PASSWORD</label>
                <Link to="/forgot-password" className="auth-forgot">Forgot Password?</Link>
              </div>
              <div className="auth-input-wrap">
                <input
                  id="password"
                  className="auth-input auth-input--password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="auth-eye"
                  onClick={() => setShowPassword(v => !v)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className={`auth-submit ${loading ? 'auth-submit--loading' : ''}`}
              disabled={loading}
            >
              {loading ? <span className="auth-spinner" /> : 'Sign In'}
            </button>
          </form>

          <div className="auth-divider">
            <span>OR CONTINUE WITH</span>
          </div>

          <div className="auth-social">
            <button className="auth-social-btn">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
                <path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 0 0 9 18z" fill="#34A853"/>
                <path d="M3.964 10.71A5.41 5.41 0 0 1 3.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 0 0 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
                <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 0 0 .957 4.958L3.964 6.29C4.672 4.163 6.656 3.58 9 3.58z" fill="#EA4335"/>
              </svg>
              Google
            </button>
            <button className="auth-social-btn">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <rect width="18" height="18" rx="3" fill="#1877F2"/>
                <path d="M12.5 9H10V7.5c0-.552.448-.5 1-.5h1V5h-1.5C9.12 5 8 6.12 8 7.5V9H6.5v2.5H8V18h2.5v-6.5H12l.5-2.5z" fill="white"/>
              </svg>
              Facebook
            </button>
          </div>

          <p className="auth-switch">
            New to ClauseWise?{' '}
            <Link to="/register" className="auth-switch__link">Create an account</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
