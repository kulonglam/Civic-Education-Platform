import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { tenantStore } from '../lib/api';
import { authService } from '../lib/services';
import { extractError } from '../lib/api';
import { Alert, PasswordInput } from '../components/ui';
import { PlatformLogo } from '../components/PlatformLogo';
import { BookOpen, AcademicCap, ShieldCheck } from '../components/Icons';

const API_ORIGIN = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api').replace(/\/api\/?$/, '');

const BRAND_FEATURES = [
  { Icon: BookOpen,     key: 'home.featureLearnTitle',  desc: 'home.featureLearnText' },
  { Icon: AcademicCap, key: 'home.featureQuizTitle',   desc: 'home.featureQuizText' },
  { Icon: ShieldCheck, key: 'home.featureForumTitle',  desc: 'home.featureForumText' },
];

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

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const result = await login(email, password);
      if (result?.mfaRequired) {
        setMfaToken(result.mfaToken);
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

  const submitMfa = async (e) => {
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
    <div className="mx-auto max-w-md">
      <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-md dark:border-slate-700 dark:bg-slate-800">
        {/* Brand header */}
        <div className="bg-gradient-to-br from-brand-700 to-brand-900 px-8 py-8 text-white">
          <div className="flex items-center gap-3">
            <PlatformLogo className="h-12 w-12 rounded-lg bg-white/10 p-1" />
            <div>
              <p className="font-bold">{t('app.name')}</p>
              <p className="text-xs text-brand-200">{t('app.tagline')}</p>
            </div>
          </div>
          <div className="mt-6 space-y-3">
            {BRAND_FEATURES.map(({ Icon, key }) => (
              <div key={key} className="flex items-center gap-2 text-sm text-brand-100">
                <Icon className="h-4 w-4 shrink-0 text-brand-300" />
                {t(key)}
              </div>
            ))}
          </div>
        </div>

        {/* Form */}
        <div className="px-8 py-6">
          <h1 className="mb-1 text-xl font-bold text-gray-900 dark:text-slate-100">
            {mfaStep ? t('auth.mfaTitle') : t('auth.loginTitle')}
          </h1>
          {!mfaStep && (
            <p className="mb-5 text-sm text-gray-500 dark:text-slate-400">
              {t('auth.noAccount')}{' '}
              <Link to="/register" className="text-brand-600 hover:underline dark:text-brand-400">
                {t('nav.register')}
              </Link>
            </p>
          )}
          {mfaStep && (
            <p className="mb-5 text-sm text-gray-500 dark:text-slate-400">
              {t('auth.mfaSubtitle')}
            </p>
          )}

          {error && (
            <div className="mb-4">
              <Alert>{error}</Alert>
            </div>
          )}

          {!mfaStep && ssoAvailable && (
            <div className="mb-4">
              <button type="button" className="btn-secondary w-full" onClick={startSso}>
                {t('auth.ssoLogin')}
              </button>
              <div className="my-4 flex items-center gap-3">
                <hr className="flex-1 border-gray-200 dark:border-slate-700" />
                <span className="text-xs text-gray-400 dark:text-slate-500">{t('misc.orContinueWith')}</span>
                <hr className="flex-1 border-gray-200 dark:border-slate-700" />
              </div>
            </div>
          )}

          {mfaStep ? (
            <form onSubmit={submitMfa} className="space-y-4">
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
            <form onSubmit={submit} className="space-y-4">
              <div>
                <label className="label" htmlFor="email">{t('auth.email')}</label>
                <input
                  id="email"
                  type="email"
                  className="input"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                  required
                />
              </div>
              <div>
                <div className="flex items-center justify-between">
                  <label className="label mb-0" htmlFor="password">{t('auth.password')}</label>
                  <Link to="/forgot-password" className="text-xs text-brand-600 hover:underline dark:text-brand-400">
                    {t('auth.forgotPassword')}
                  </Link>
                </div>
                <PasswordInput
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  className="mt-1"
                  required
                />
              </div>
              <button type="submit" className="btn-primary w-full" disabled={loading}>
                {loading ? t('common.loading') : t('nav.login')}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export { LoginPage };
