/**
 * Server-side content bundle downloader.
 *
 * Downloads a full study pack from /api/v1/content-bundle/ and stores
 * every article/quiz/category in IndexedDB so the app works fully offline.
 *
 * Usage:
 *   import { downloadContentBundle } from './contentBundle';
 *   const result = await downloadContentBundle();
 *   toast.success(`Downloaded ${result.articles} articles for offline use`);
 */

import { api } from '../api';
import { getDb, scopeKey, setEntry } from './db';

export async function downloadContentBundle({ categoryId } = {}) {
  const params = categoryId ? { category_id: categoryId } : {};
  const { data } = await api.get('/content-bundle/', { params });

  const db = await getDb();
  const tx = db.transaction(
    ['articles', 'article_lists', 'categories', 'quizzes'],
    'readwrite',
  );

  // Cache each article individually
  for (const article of data.articles || []) {
    await tx.objectStore('articles').put({ key: scopeKey(article.id), data: article });
  }

  // Cache article list snapshot
  await tx.objectStore('article_lists').put({
    key: scopeKey('bundle'),
    data: data.articles || [],
  });

  // Cache categories
  for (const cat of data.categories || []) {
    await tx.objectStore('categories').put({ key: scopeKey(cat.id), data: cat });
  }

  // Cache quizzes
  for (const quiz of data.quizzes || []) {
    await tx.objectStore('quizzes').put({ key: scopeKey(quiz.id), data: quiz });
  }

  await tx.done;

  return {
    articles: (data.articles || []).length,
    quizzes: (data.quizzes || []).length,
    categories: (data.categories || []).length,
    generatedAt: data.generated_at,
  };
}
