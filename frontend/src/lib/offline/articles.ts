import { articleService, categoryService } from '../services';
import { getEntry, scopeKey, setEntry } from './db';

function listCacheKey(params) {
  const sorted = Object.keys(params)
    .sort()
    .map((k) => `${k}=${params[k]}`)
    .join('&');
  return scopeKey(`list:${sorted || 'default'}`);
}

async function fetchOrCache(cacheKey, storeName, fetcher) {
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
    return data.results ?? data;
  });
}

export async function loadArticlesList(params) {
  const cacheKey = listCacheKey(params);
  return fetchOrCache(cacheKey, 'article_lists', async () => {
    const { data } = await articleService.list(params);
    for (const article of data.results ?? []) {
      await setEntry('articles', scopeKey(article.id), article);
    }
    return data;
  });
}

export async function loadArticle(id) {
  const cacheKey = scopeKey(id);
  return fetchOrCache(cacheKey, 'articles', async () => {
    const { data } = await articleService.get(id);
    return data;
  });
}
