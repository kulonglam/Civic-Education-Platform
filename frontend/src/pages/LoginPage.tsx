import { useEffect, useState, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { tenantStore } from '../lib/api';
import { authService } from '../lib/services';
import { extractError } from '../lib/api';
import { Alert, PasswordInput } from '../components/ui';
import { AuthShell } from '../components/AuthShell';

const API_ORIGIN = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api').replace(/\/api\/?$/, '');

function LoginPage() {
  const { t } = useTranslation();
  const { login, verifyMfaLogin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from ?? '/';
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [mfaToken, setMfaToken] = useState('');
  const [mfaCode, setMfaCode] = useState('');
  const [mfaStep, setMfaStep] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [ssoAvailable, setSsoAvailable] = useState(false);

  useEffect(() => {
    const org = tenantStore.slug;
    if (!org) return;
    authService
      .ssoStatus(org)
      .then(({ data }) => setSsoAvailable(Boolean(data.configured && data.enabled_for_org)))
      .catch(() => setSsoAvailable(false));
  }, []);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const result = await login(email, password);
      if (result?.mfaRequired) {
        setMfaToken(result.mfaToken ?? '');
        setMfaStep(true);
        return;
      }
      navigate(from, { replace: true });
    } catch (err) {
      setError(extractError(err));
    } finally {
      setLoading(false);
    }
  };

  const submitMfa = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await verifyMfaLogin(mfaToken, mfaCode.trim());
      navigate(from, { replace: true });
    } catch (err) {
      setError(extractError(err));
    } finally {
      setLoading(false);
    }
  };

  const startSso = () => {
    const org = tenantStore.slug;
    if (!org) return;
    window.location.assign(`${API_ORIGIN}/api/auth/sso/login/?org=${encodeURIComponent(org)}`);
  };

  return (
    <AuthShell
      title={mfaStep ? t('auth.mfaTitle') : t('auth.loginPanelTitle')}
      subtitle={mfaStep ? t('auth.mfaSubtitle') : t('auth.loginPanelSubtitle')}
      showBrand={false}
    >
      <p className="eyebrow">{t('auth.secureAccess')}</p>
      <h2 className="mt-2 font-display text-2xl font-semibold text-ink-900 dark:text-slate-50">
        {mfaStep ? t('auth.mfaTitle') : t('auth.loginTitle')}
      </h2>
      {!mfaStep && (
        <p className="mt-2 text-sm text-ink-700/70 dark:text-slate-400">
          {t('auth.noAccount')}{' '}
          <Link to="/register" className="font-semibold text-brand-700 hover:underline dark:text-brand-400">
            {t('nav.register')}
          </Link>
        </p>
      )}

      {error && (
        <div className="mt-5">
          <Alert id="login-error">{error}</Alert>
        </div>
      )}

      <div className="mt-6">
        {!mfaStep && ssoAvailable && (
          <div className="mb-5">
            <button type="button" className="btn-secondary w-full" onClick={startSso}>
              {t('auth.ssoLogin')}
            </button>
            <div className="my-5 flex items-center gap-3">
              <hr className="flex-1 border-ink-100 dark:border-slate-700" />
              <span className="text-xs font-medium uppercase tracking-wide text-ink-700/70 dark:text-slate-500">
                {t('misc.orContinueWith')}
              </span>
              <hr className="flex-1 border-ink-100 dark:border-slate-700" />
            </div>
          </div>
        )}

        {mfaStep ? (
          <form onSubmit={submitMfa} className="space-y-4" aria-describedby={error ? 'login-error' : undefined}>
            <div>
              <label className="label" htmlFor="mfa-code">{t('auth.mfaCode')}</label>
              <input
                id="mfa-code"
                className="input"
                inputMode="numeric"
                autoComplete="one-time-code"
                maxLength={6}
                value={mfaCode}
                onChange={(e) => setMfaCode(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading || mfaCode.trim().length < 6}>
              {loading ? t('common.loading') : t('auth.mfaVerify')}
            </button>
            <button
              type="button"
              className="btn-secondary w-full"
              onClick={() => {
                setMfaStep(false);
                setMfaToken('');
                setMfaCode('');
                setError('');
              }}
            >
              {t('auth.mfaBack')}
            </button>
          </form>
        ) : (
          <form onSubmit={submit} className="space-y-4" aria-describedby={error ? 'login-error' : undefined}>
            <div>
              <label className="label" htmlFor="email">{t('auth.email')}</label>
              <input
                id="email"
                type="email"
                className="input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                aria-invalid={Boolean(error)}
                aria-describedby={error ? 'login-error' : undefined}
                autoComplete="email"
                required
              />
            </div>
            <div>
              <div className="flex items-center justify-between">
                <label className="label mb-0" htmlFor="password">{t('auth.password')}</label>
                <Link to="/forgot-password" className="text-xs font-semibold text-brand-700 hover:underline dark:text-brand-400">
                  {t('auth.forgotPassword')}
                </Link>
              </div>
              <PasswordInput
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                className="mt-1.5"
                aria-invalid={Boolean(error)}
                aria-describedby={error ? 'login-error' : undefined}
                required
              />
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? t('common.loading') : t('nav.login')}
            </button>
          </form>
        )}
      </div>
    </AuthShell>
  );
}

export { LoginPage };
