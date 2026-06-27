import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { tokenStore, tenantStore } from '../lib/api';
import { Alert, Spinner } from '../components/ui';

export function SsoCallbackPage() {
  const { t } = useTranslation();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const [error, setError] = useState('');

  useEffect(() => {
    const ssoError = params.get('error');
    if (ssoError) {
      setError(ssoError);
      return;
    }

    const access = params.get('access');
    const refresh = params.get('refresh');
    const org = params.get('org');
    if (!access) {
      setError(t('auth.ssoMissingTokens'));
      return;
    }

    tokenStore.set(access, refresh);
    if (org) {
      tenantStore.set(org);
    }

    refreshUser()
      .then(() => navigate('/', { replace: true }))
      .catch(() => setError(t('auth.ssoFailed')));
  }, [navigate, params, refreshUser, t]);

  if (error) {
    return (
      <div className="mx-auto max-w-md">
        <div className="card">
          <Alert>{error}</Alert>
          <Link to="/login" className="btn-primary mt-4 inline-block">
            {t('nav.login')}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-md">
      <div className="card text-center">
        <Spinner />
        <p className="mt-4 text-sm text-gray-600">{t('auth.ssoCompleting')}</p>
      </div>
    </div>
  );
}
