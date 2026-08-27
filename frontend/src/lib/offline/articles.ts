import { articleService, categoryService } from '../services';
import { unwrapList } from '../../types/api';
import type { Id, QueryParams } from '../../types/api';
import { getEntry, scopeKey, setEntry } from './db';

function listCacheKey(params: QueryParams = {}) {
  const sorted = Object.keys(params)
    .sort()
    .map((k) => `${k}=${params[k]}`)
    .join('&');
  return scopeKey(`list:${sorted || 'default'}`);
}

async function fetchOrCache<T>(cacheKey: string, storeName: string, fetcher: () => Promise<T>) {
  try {
    const data = await fetcher();
    await setEntry(storeName, cacheKey, data);
    return { data, source: 'network' };
  } catch (error) {
    const cached = await getEntry(storeName, cacheKey);
    if (cached) {
      return { data: cached, source: 'cache' };
    }
    throw error;
  }
}

export async function loadCategories() {
  const cacheKey = scopeKey('categories');
  return fetchOrCache(cacheKey, 'categories', async () => {
    const { data } = await categoryService.list();
    return unwrapList(data);
  });
}

export async function loadArticlesList(params: QueryParams = {}) {
  const cacheKey = listCacheKey(params);
  return fetchOrCache(cacheKey, 'article_lists', async () => {
    const { data } = await articleService.list(params);
    for (const article of unwrapList(data)) {
      await setEntry('articles', scopeKey(article.id), article);
    }
    return data;
  });
}

export async function loadArticle(id: Id | undefined) {
  const cacheKey = scopeKey(id ?? '');
  return fetchOrCache(cacheKey, 'articles', async () => {
    const { data } = await articleService.get(id);
    return data;
  });
}
