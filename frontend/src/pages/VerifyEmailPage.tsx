import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { authService } from '../lib/services';
import { Alert, Spinner } from '../components/ui';
import { AuthShell } from '../components/AuthShell';
import { PlatformLogo } from '../components/PlatformLogo';

export function VerifyEmailPage() {
  const { t } = useTranslation();
  const { token } = useParams();
  const [status, setStatus] = useState('loading');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      return;
    }
    authService.verifyEmail(token)
      .then(() => setStatus('success'))
      .catch(() => setStatus('error'));
  }, [token]);

  const title =
    status === 'success' ? t('auth.verifySuccess') : status === 'error' ? t('auth.verifyFailed') : t('auth.verifying');

  return (
    <AuthShell title={title} subtitle={t('app.tagline')}>
      <div className="mb-6 flex items-center gap-3 lg:hidden">
        <PlatformLogo className="h-10 w-10" />
        <div>
          <p className="font-display text-lg font-semibold text-ink-900 dark:text-slate-100">{t('app.name')}</p>
          <p className="text-xs text-ink-700/60 dark:text-slate-400">{t('app.tagline')}</p>
        </div>
      </div>

      <p className="eyebrow">{t('auth.secureAccess')}</p>
      <h2 className="mt-2 font-display text-2xl font-semibold text-ink-900 dark:text-slate-50">{title}</h2>

      <div className="mt-6">
        {status === 'loading' && <Spinner label={t('auth.verifying')} />}
        {status === 'success' && (
          <>
            <Alert kind="success">{t('auth.verifySuccess')}</Alert>
            <Link to="/login" className="btn-primary mt-4 inline-flex w-full justify-center">
              {t('nav.login')}
            </Link>
          </>
        )}
        {status === 'error' && (
          <>
            <Alert>{t('auth.verifyFailed')}</Alert>
            <Link to="/register" className="btn-secondary mt-4 inline-flex w-full justify-center">
              {t('nav.register')}
            </Link>
          </>
        )}
      </div>
    </AuthShell>
  );
}
