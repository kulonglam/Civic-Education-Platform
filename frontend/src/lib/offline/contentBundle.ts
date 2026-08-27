import { api } from '../api';
import type { ContentBundleMeta, QueryParams } from '../../types/api';
import { getEntry, scopeKey, setEntry } from './db';

/**
 * Download a full offline study pack from GET /content-bundle/ and cache
 * articles, quizzes, media metadata, and categories in IndexedDB for offline reading.
 */
export async function downloadContentBundle({ categoryId }: { categoryId?: string | number } = {}) {
  const params: QueryParams = {};
  if (categoryId) params.category_id = categoryId;

  const { data } = await api.get<{
    categories?: unknown[];
    articles?: Array<{ id: string }>;
    quizzes?: Array<{ id: string }>;
    media?: Array<{ id: string }>;
    generated_at?: string | null;
  }>('/content-bundle/', { params });
  const categories = data.categories ?? [];
  const articles = data.articles ?? [];
  const quizzes = data.quizzes ?? [];
  const media = data.media ?? [];

  await setEntry('categories', scopeKey('categories'), categories);

  for (const article of articles) {
    await setEntry('articles', scopeKey(article.id), article);
  }

  await setEntry('article_lists', scopeKey('list:default'), {
    count: articles.length,
    results: articles,
  });

  for (const quiz of quizzes) {
    await setEntry('quizzes', scopeKey(quiz.id), quiz);
  }

  for (const item of media) {
    await setEntry('media', scopeKey(item.id), item);
  }
  await setEntry('media', scopeKey('list:default'), {
    count: media.length,
    results: media,
  });

  const summary: ContentBundleMeta = {
    articles: articles.length,
    quizzes: quizzes.length,
    media: media.length,
    categories: categories.length,
    generatedAt: data.generated_at ?? null,
  };
  await setEntry('categories', scopeKey('bundle:meta'), summary);
  return summary;
}

export async function getContentBundleMeta() {
  return getEntry<ContentBundleMeta>('categories', scopeKey('bundle:meta'));
}
