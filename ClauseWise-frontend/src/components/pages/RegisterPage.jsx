import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Check, X } from 'lucide-react';
import './AuthPage.css';

function PasswordStrength({ password }) {
  const checks = [
    { label: 'At least 8 characters', pass: password.length >= 8 },
    { label: 'Contains a symbol', pass: /[^a-zA-Z0-9]/.test(password) },
    { label: 'Contains a number', pass: /\d/.test(password) },
  ];
  const score = checks.filter(c => c.pass).length;
  const colors = ['', '#e8a0a0', '#f0c060', '#a3d4b5'];
  const labels = ['', 'Weak', 'Fair', 'Strong'];

  if (!password) return null;

  return (
    <div className="pw-strength">
      <div className="pw-strength__bar">
        {[1, 2, 3].map(i => (
          <div
            key={i}
            className="pw-strength__segment"
            style={{ background: i <= score ? colors[score] : 'var(--border)' }}
          />
        ))}
        <span className="pw-strength__label" style={{ color: colors[score] }}>
          {labels[score]}
        </span>
      </div>
      <ul className="pw-checks">
        {checks.map((c, i) => (
          <li key={i} className={`pw-check ${c.pass ? 'pw-check--pass' : ''}`}>
            {c.pass ? <Check size={12} /> : <X size={12} />}
            {c.label}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));

  const validate = () => {
    const errs = {};
    if (!form.name.trim()) errs.name = 'Full name is required.';
    if (!form.email.includes('@')) errs.email = 'Enter a valid email address.';
    if (form.password.length < 8) errs.password = 'Password must be at least 8 characters.';
    if (!/[^a-zA-Z0-9]/.test(form.password)) errs.password = 'Password must contain a symbol.';
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setErrors({});
    setLoading(true);
    // Simulate account creation — replace with your real API call
    await new Promise(r => setTimeout(r, 1400));
    setLoading(false);
    navigate('/documents');
  };

  return (
    <div className="auth-page">
      <div className="auth-main">
      <main className="auth-main">
        <div className="auth-card auth-card--register">
          <div className="auth-card__header">
            <h1 className="auth-card__title">Join ClauseWise</h1>
            <p className="auth-card__sub">Secure your professional legacy today.</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit} noValidate>
            <div className="auth-field">
              <label className="auth-label" htmlFor="name">FULL NAME</label>
              <input
                id="name"
                className={`auth-input ${errors.name ? 'auth-input--error' : ''}`}
                type="text"
                placeholder="John Doe"
                value={form.name}
                onChange={set('name')}
                autoComplete="name"
              />
              {errors.name && <span className="auth-field-error">{errors.name}</span>}
            </div>

            <div className="auth-field">
              <label className="auth-label" htmlFor="reg-email">EMAIL ADDRESS</label>
              <input
                id="reg-email"
                className={`auth-input ${errors.email ? 'auth-input--error' : ''}`}
                type="email"
                placeholder="name@company.com"
                value={form.email}
                onChange={set('email')}
                autoComplete="email"
              />
              {errors.email && <span className="auth-field-error">{errors.email}</span>}
            </div>

            <div className="auth-field">
              <label className="auth-label" htmlFor="reg-password">PASSWORD</label>
              <div className="auth-input-wrap">
                <input
                  id="reg-password"
                  className={`auth-input auth-input--password ${errors.password ? 'auth-input--error' : ''}`}
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={form.password}
                  onChange={set('password')}
                  autoComplete="new-password"
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
              {errors.password
                ? <span className="auth-field-error">{errors.password}</span>
                : <span className="auth-hint">Must be at least 8 characters with a symbol.</span>
              }
              <PasswordStrength password={form.password} />
            </div>

            <button
              type="submit"
              className={`auth-submit ${loading ? 'auth-submit--loading' : ''}`}
              disabled={loading}
            >
              {loading ? <span className="auth-spinner" /> : 'Create Account'}
            </button>
          </form>

          <div className="auth-divider">
            <span>CONTINUE WITH</span>
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

          <p className="auth-terms">
            By clicking "Create Account", you agree to ClauseWise's{' '}
            <Link to="/terms">Terms of Service</Link> and{' '}
            <Link to="/privacy">Privacy Policy</Link>.
          </p>
        </div>
      </main>
      </div>
    </div>
  );
}
