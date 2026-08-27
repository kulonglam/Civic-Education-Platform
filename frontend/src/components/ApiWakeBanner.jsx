import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { API_READY_EVENT, API_SLOW_MS, API_WAKE_EVENT, pingApiReady } from '../lib/apiHealth';

function ApiWakeBanner() {
  const { t } = useTranslation();
  const [waking, setWaking] = useState(false);

  useEffect(() => {
    let cancelled = false;
    let slowTimer;
    let retryTimer;

    const markReady = () => {
      if (cancelled) return;
      setWaking(false);
    };

    const markWaking = () => {
      if (cancelled) return;
      setWaking(true);
    };

    const probe = async () => {
      slowTimer = window.setTimeout(markWaking, API_SLOW_MS);
      try {
        await pingApiReady();
        markReady();
      } catch {
        markWaking();
        retryTimer = window.setTimeout(probe, 4000);
      } finally {
        window.clearTimeout(slowTimer);
      }
    };

    window.addEventListener(API_WAKE_EVENT, markWaking);
    window.addEventListener(API_READY_EVENT, markReady);
    probe();

    return () => {
      cancelled = true;
      window.clearTimeout(slowTimer);
      window.clearTimeout(retryTimer);
      window.removeEventListener(API_WAKE_EVENT, markWaking);
      window.removeEventListener(API_READY_EVENT, markReady);
    };
  }, []);

  if (!waking) return null;

  return (
    <div
      className="border-b border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-950 dark:border-amber-900/40 dark:bg-amber-950/40 dark:text-amber-100"
      role="status"
    >
      <p className="mx-auto max-w-6xl">{t('errors.apiWaking')}</p>
    </div>
  );
}

export { ApiWakeBanner };
