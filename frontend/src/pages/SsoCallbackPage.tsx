// @ts-nocheck
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { tokenStore, tenantStore } from '../lib/api';
import { Alert, Spinner } from '../components/ui';

function readHashParams() {
  const hash = window.location.hash.replace(/^#/, '');
  return new URLSearchParams(hash);
}

export function SsoCallbackPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const [error, setError] = useState('');

  useEffect(() => {
    const params = readHashParams();
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
  }, [navigate, refreshUser, t]);

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
        <p className="mt-4 text-sm text-ink-700/70 dark:text-slate-400">{t('auth.ssoCompleting')}</p>
      </div>
    </div>
  );
}
