import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { authService } from '../lib/services';
import { useAuth } from '../context/AuthContext';
import { extractError } from '../lib/api';
import { Alert } from './ui';

export function EmailVerifyBanner() {
  const { t } = useTranslation();
  const { user, refreshUser } = useAuth();
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  if (!user || user.email_verified) return null;

  const resend = async () => {
    setBusy(true);
    setError('');
    setMessage('');
    try {
      const { data } = await authService.resendVerification();
      setMessage(data.message || t('verify.resendSent'));
      await refreshUser();
    } catch (err) {
      setError(extractError(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="border-b border-amber-200 bg-amber-50 px-4 py-3">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-amber-900">{t('verify.bannerTitle')}</p>
          <p className="text-xs text-amber-800">{t('verify.bannerHint')}</p>
          {message && <p className="mt-1 text-xs text-green-700">{message}</p>}
          {error && <p className="mt-1 text-xs text-red-700">{error}</p>}
        </div>
        <button type="button" className="btn-secondary text-sm" onClick={resend} disabled={busy}>
          {busy ? t('common.loading') : t('verify.resend')}
        </button>
      </div>
    </div>
  );
}
