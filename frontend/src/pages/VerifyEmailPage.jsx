import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { authService } from '../lib/services';
import { Alert, Spinner } from '../components/ui';

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

  return (
    <div className="mx-auto max-w-md py-8">
      <div className="card text-center">
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
    </div>
  );
}
