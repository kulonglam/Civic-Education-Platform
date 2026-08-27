import { openDB, type IDBPDatabase } from 'idb';
import { tenantStore } from '../api';

const DB_NAME = 'cep-offline';
const DB_VERSION = 3;

export type OfflineStoreName =
  | 'articles'
  | 'article_lists'
  | 'categories'
  | 'quizzes'
  | 'quiz_queue'
  | 'write_queue'
  | 'media';

let dbPromise: Promise<IDBPDatabase> | undefined;

function scopeKey(suffix: string | number) {
  return `${tenantStore.slug || 'default'}:${suffix}`;
}

async function getDb() {
  if (!dbPromise) {
    dbPromise = openDB(DB_NAME, DB_VERSION, {
      upgrade(db, oldVersion) {
        if (oldVersion < 1) {
          db.createObjectStore('articles', { keyPath: 'key' });
          db.createObjectStore('article_lists', { keyPath: 'key' });
          db.createObjectStore('categories', { keyPath: 'key' });
          db.createObjectStore('quizzes', { keyPath: 'key' });
          db.createObjectStore('quiz_queue', { keyPath: 'id', autoIncrement: true });
        }
        if (oldVersion < 2) {
          const writeQueue = db.createObjectStore('write_queue', {
            keyPath: 'id',
            autoIncrement: true,
          });
          writeQueue.createIndex('type', 'type', { unique: false });
        }
        if (oldVersion < 3) {
          db.createObjectStore('media', { keyPath: 'key' });
        }
      },
    });
  }
  return dbPromise;
}

async function getEntry<T = unknown>(storeName: OfflineStoreName, key: string): Promise<T | null> {
  const db = await getDb();
  const row = await db.get(storeName, key);
  return (row?.data as T | undefined) ?? null;
}

async function setEntry(storeName: OfflineStoreName, key: string, data: unknown) {
  const db = await getDb();
  await db.put(storeName, { key, data, cachedAt: Date.now() });
}

export { getDb, scopeKey, getEntry, setEntry };
