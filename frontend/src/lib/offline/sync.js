import { flushQuizQueue } from './quizzes';
import { flushWriteQueue } from './writes';

export function startOfflineSync() {
  const run = () => {
    flushQuizQueue().catch(() => {});
    flushWriteQueue().catch(() => {});
  };

  window.addEventListener('online', run);

  // Handle Background Sync messages forwarded from the service worker
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('message', (evt) => {
      if (evt.data?.type === 'cep:bg-sync') {
        run();
      }
    });
  }

  run();
  return () => window.removeEventListener('online', run);
}
