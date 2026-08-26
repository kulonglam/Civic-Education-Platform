import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useOnlineStatus } from '../hooks/useOnlineStatus';
import { getQueuedQuizCount } from '../lib/offline/quizzes';

function OfflineBanner() {
  const { t } = useTranslation();
  const online = useOnlineStatus();
  const [queuedCount, setQueuedCount] = useState(0);

  useEffect(() => {
    const refresh = () => {
      getQueuedQuizCount()
        .then(setQueuedCount)
        .catch(() => setQueuedCount(0));
    };
    refresh();
    window.addEventListener('cep:quiz-queue-flushed', refresh);
    window.addEventListener('online', refresh);
    return () => {
      window.removeEventListener('cep:quiz-queue-flushed', refresh);
      window.removeEventListener('online', refresh);
    };
  }, []);

  if (online && queuedCount === 0) {
    return null;
  }

  return (
    <div
      className={`border-b px-4 py-2 text-sm ${
        online
          ? 'border-brand-200 bg-brand-50 text-brand-900 dark:border-brand-900/40 dark:bg-brand-950/40 dark:text-brand-200'
          : 'border-amber-200 bg-amber-50 text-amber-900 dark:border-amber-900/40 dark:bg-amber-950/40 dark:text-amber-200'
      }`}
      role="status"
    >
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-2">
        <span>
          {!online
            ? t('offline.banner')
            : t('offline.syncedBanner', { count: queuedCount })}
        </span>
        {queuedCount > 0 && (
          <Link to="/quizzes/results" className="font-medium underline">
            {t('offline.viewResults')}
          </Link>
        )}
      </div>
    </div>
  );
}

export { OfflineBanner };
