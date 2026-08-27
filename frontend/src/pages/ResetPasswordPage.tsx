import { useState, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useSearchParams } from 'react-router-dom';
import { authService } from '../lib/services';
import { extractError } from '../lib/api';
import { Alert, PasswordInput } from '../components/ui';
import { AuthShell } from '../components/AuthShell';
import { PlatformLogo } from '../components/PlatformLogo';

export function ResetPasswordPage() {
  const { t } = useTranslation();
  const [params] = useSearchParams();
  const uid = params.get('uid') ?? '';
  const token = params.get('token') ?? '';
  const otpMode = params.get('mode') === 'otp' || (!uid && !token);

  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (otpMode) {
        await authService.confirmResetOtp(phone, code, password);
      } else {
        await authService.confirmReset(uid, token, password);
      }
      setDone(true);
    } catch (err) {
      setError(extractError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell title={t('auth.resetTitle')} subtitle={t('auth.resetSubtitle')}>
      <div className="mb-6 flex items-center gap-3 lg:hidden">
        <PlatformLogo className="h-10 w-10" />
        <div>
          <p className="font-display text-lg font-semibold text-ink-900 dark:text-slate-100">{t('app.name')}</p>
          <p className="text-xs text-ink-700/60 dark:text-slate-400">{t('app.tagline')}</p>
        </div>
      </div>

      <p className="eyebrow">{t('auth.secureAccess')}</p>
      <h2 className="mt-2 font-display text-2xl font-semibold text-ink-900 dark:text-slate-50">
        {t('auth.resetTitle')}
      </h2>
      <p className="mt-2 text-sm text-ink-700/70 dark:text-slate-400">{t('auth.resetSubtitle')}</p>

      <div className="mt-6">
        {done ? (
          <>
            <Alert kind="success">{t('auth.verifySuccess')}</Alert>
            <Link to="/login" className="btn-primary mt-4 block w-full text-center">
              {t('nav.login')}
            </Link>
          </>
        ) : (
          <>
            {error && (
              <div className="mb-4">
              <Alert id="reset-confirm-error">{error}</Alert>
              </div>
            )}
            <form onSubmit={submit} className="space-y-4" aria-describedby={error ? 'reset-confirm-error' : undefined}>
              {otpMode && (
                <>
                  <div>
                    <label className="label" htmlFor="reset-phone">{t('profile.phone')}</label>
                    <input
                      id="reset-phone"
                      type="tel"
                      className="input"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      autoComplete="tel"
                      required
                    />
                  </div>
                  <div>
                    <label className="label" htmlFor="reset-otp">{t('sms.otpCode')}</label>
                    <input
                      id="reset-otp"
                      className="input"
                      value={code}
                      onChange={(e) => setCode(e.target.value)}
                      inputMode="numeric"
                      autoComplete="one-time-code"
                      required
                      maxLength={6}
                    />
                  </div>
                </>
              )}
              <div>
                <label className="label" htmlFor="reset-password">{t('auth.newPassword')}</label>
                <PasswordInput
                  id="reset-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="new-password"
                  minLength={8}
                  aria-invalid={Boolean(error)}
                  aria-describedby={error ? 'reset-confirm-error' : undefined}
                  required
                />
              </div>
              <button type="submit" className="btn-primary w-full" disabled={loading}>
                {loading ? t('common.loading') : t('common.submit')}
              </button>
            </form>
          </>
        )}
      </div>
    </AuthShell>
  );
}
