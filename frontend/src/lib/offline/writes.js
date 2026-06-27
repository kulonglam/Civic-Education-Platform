/**
 * Offline write queue for forum posts and profile edits.
 *
 * When the network is unavailable, mutations are stored in IndexedDB and
 * replayed automatically when the user comes back online.
 *
 * Supported write types:
 *  - 'forum_post'   { topicId, body }
 *  - 'forum_topic'  { title, body, categoryId }
 *  - 'profile_edit' { fields: { ... } }
 */

import { api } from '../api';
import { getDb } from './db';

export async function queueWrite(type, payload) {
  const db = await getDb();
  const id = await db.add('write_queue', {
    type,
    payload,
    queuedAt: Date.now(),
    attempts: 0,
  });
  // Register a Background Sync tag so the SW can replay when online
  if ('serviceWorker' in navigator && 'SyncManager' in window) {
    const reg = await navigator.serviceWorker.ready;
    await reg.sync.register('cep-write-queue').catch(() => {});
  }
  return id;
}

export async function getPendingWriteCount() {
  const db = await getDb();
  return db.count('write_queue');
}

export async function flushWriteQueue() {
  if (!navigator.onLine) return { synced: 0, pending: await getPendingWriteCount() };

  const db = await getDb();
  const items = await db.getAll('write_queue');
  let synced = 0;

  for (const item of items) {
    try {
      await _replay(item);
      await db.delete('write_queue', item.id);
      synced += 1;
    } catch {
      // Leave in queue; will retry on next flush
      await db.put('write_queue', { ...item, attempts: (item.attempts || 0) + 1 });
      break;
    }
  }

  const pending = await getPendingWriteCount();
  if (synced > 0) {
    window.dispatchEvent(new CustomEvent('cep:write-queue-flushed', { detail: { synced, pending } }));
  }
  return { synced, pending };
}

async function _replay(item) {
  switch (item.type) {
    case 'forum_post':
      return api.post(`/forum/topics/${item.payload.topicId}/posts/`, { body: item.payload.body });
    case 'forum_topic':
      return api.post('/forum/topics/', {
        title: item.payload.title,
        body: item.payload.body,
        category: item.payload.categoryId,
      });
    case 'profile_edit':
      return api.patch('/accounts/profile/', item.payload.fields);
    default:
      throw new Error(`Unknown write type: ${item.type}`);
  }
}
