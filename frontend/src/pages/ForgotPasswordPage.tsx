import { useState, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { authService } from '../lib/services';
import { extractError } from '../lib/api';
import { Alert } from '../components/ui';
import { AuthShell } from '../components/AuthShell';
import { PlatformLogo } from '../components/PlatformLogo';

export function ForgotPasswordPage() {
  const { t } = useTranslation();
  const [mode, setMode] = useState('email');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submitEmail = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authService.requestReset(email);
      setSent(true);
    } catch (err) {
      setError(extractError(err));
    } finally {
      setLoading(false);
    }
  };

  const submitPhone = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authService.requestResetOtp(phone);
      setSent(true);
    } catch (err) {
      setError(extractError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell title={t('auth.resetRequestTitle')} subtitle={t('auth.resetRequestSubtitle')}>
      <div className="mb-6 flex items-center gap-3 lg:hidden">
        <PlatformLogo className="h-10 w-10" />
        <div>
          <p className="font-display text-lg font-semibold text-ink-900 dark:text-slate-100">{t('app.name')}</p>
          <p className="text-xs text-ink-700/60 dark:text-slate-400">{t('app.tagline')}</p>
        </div>
      </div>

      <p className="eyebrow">{t('auth.secureAccess')}</p>
      <h2 className="mt-2 font-display text-2xl font-semibold text-ink-900 dark:text-slate-50">
        {t('auth.resetRequestTitle')}
      </h2>
      <p className="mt-2 text-sm text-ink-700/70 dark:text-slate-400">{t('auth.resetRequestSubtitle')}</p>

      <div className="mt-6 mb-4 flex gap-2">
        <button
          type="button"
          className={mode === 'email' ? 'btn-primary flex-1' : 'btn-secondary flex-1'}
          onClick={() => {
            setMode('email');
            setSent(false);
            setError('');
          }}
        >
          {t('auth.email')}
        </button>
        <button
          type="button"
          className={mode === 'phone' ? 'btn-primary flex-1' : 'btn-secondary flex-1'}
          onClick={() => {
            setMode('phone');
            setSent(false);
            setError('');
          }}
        >
          {t('profile.phone')}
        </button>
      </div>

      {sent ? (
        <Alert kind="success">
          {mode === 'email' ? t('auth.resetSent') : t('sms.otpSent')}
        </Alert>
      ) : (
        <>
          {error && (
            <div className="mb-4">
              <Alert id="reset-error">{error}</Alert>
            </div>
          )}
          {mode === 'email' ? (
            <form onSubmit={submitEmail} className="space-y-4" aria-describedby={error ? 'reset-error' : undefined}>
              <div>
                <label className="label" htmlFor="reset-email">{t('auth.email')}</label>
                <input
                  id="reset-email"
                  type="email"
                  className="input"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                  aria-invalid={Boolean(error)}
                  aria-describedby={error ? 'reset-error' : undefined}
                  required
                />
              </div>
              <button type="submit" className="btn-primary w-full" disabled={loading}>
                {loading ? t('common.loading') : t('auth.sendResetLink')}
              </button>
            </form>
          ) : (
            <form onSubmit={submitPhone} className="space-y-4" aria-describedby={error ? 'reset-error' : undefined}>
              <div>
                <label className="label" htmlFor="reset-phone">{t('profile.phone')}</label>
                <input
                  id="reset-phone"
                  type="tel"
                  className="input"
                  placeholder="+256772123456"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  autoComplete="tel"
                  required
                />
              </div>
              <button type="submit" className="btn-primary w-full" disabled={loading}>
                {loading ? t('common.loading') : t('sms.sendOtp')}
              </button>
              <p className="text-sm text-ink-700/60 dark:text-slate-400">{t('sms.otpResetHint')}</p>
            </form>
          )}
        </>
      )}

      {sent && mode === 'phone' && (
        <Link to="/reset-password?mode=otp" className="btn-secondary mt-4 block w-full text-center">
          {t('sms.enterOtpCode')}
        </Link>
      )}

      <p className="mt-6 text-center text-sm">
        <Link to="/login" className="font-semibold text-brand-700 hover:underline dark:text-brand-400">
          {t('common.back')}
        </Link>
      </p>
    </AuthShell>
  );
}
