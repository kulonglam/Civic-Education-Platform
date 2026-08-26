import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { notificationService } from '../lib/services';
import { useAuth } from '../context/AuthContext';
import { extractError } from '../lib/api';

const VAPID_PUBLIC_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY || '';

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const raw = window.atob(base64);
  return Uint8Array.from([...raw].map((char) => char.charCodeAt(0)));
}

export function PushNotificationPrompt() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(sessionStorage.getItem('cep:push-prompted') === '1');
  const [error, setError] = useState('');

  if (!user || done || !VAPID_PUBLIC_KEY || !('Notification' in window) || !('serviceWorker' in navigator)) {
    return null;
  }
  if (Notification.permission === 'granted' || Notification.permission === 'denied') {
    return null;
  }

  const enable = async () => {
    setBusy(true);
    setError('');
    try {
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        setDone(true);
        sessionStorage.setItem('cep:push-prompted', '1');
        return;
      }
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
      });
      const json = subscription.toJSON();
      await notificationService.subscribePush({
        endpoint: json.endpoint,
        keys: json.keys,
      });
      setDone(true);
      sessionStorage.setItem('cep:push-prompted', '1');
    } catch (err) {
      setError(extractError(err));
    } finally {
      setBusy(false);
    }
  };

  const dismiss = () => {
    sessionStorage.setItem('cep:push-prompted', '1');
    setDone(true);
  };

  return (
    <div className="border-b border-ink-100 bg-ink-50 px-4 py-3 dark:border-slate-800 dark:bg-slate-900">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-ink-900 dark:text-slate-100">{t('push.title')}</p>
          <p className="text-xs text-ink-700/80 dark:text-slate-400">{t('push.hint')}</p>
          {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
        </div>
        <div className="flex gap-2">
          <button type="button" className="btn-primary text-sm" onClick={enable} disabled={busy}>
            {busy ? t('common.loading') : t('push.enable')}
          </button>
          <button type="button" className="btn-secondary text-sm" onClick={dismiss}>
            {t('common.cancel')}
          </button>
        </div>
      </div>
    </div>
  );
}
