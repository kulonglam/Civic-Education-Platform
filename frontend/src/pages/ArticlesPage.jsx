import { useQuery } from '@tanstack/react-query';
import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useSearchParams } from 'react-router-dom';
import { Pagination } from '../components/Pagination';
import { Alert, CardSkeleton, EmptyState, PageHeader } from '../components/ui';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import { useOnlineStatus } from '../hooks/useOnlineStatus';
import { queryKeys } from '../lib/queryKeys';
import { loadArticlesList, loadCategories } from '../lib/offline/articles';
import { formatDate, readingTime } from '../lib/format';
import { localizedArticle, localizedCategory } from '../lib/localizedContent';
import { plainTextExcerpt } from '../lib/markdown';

const PAGE_SIZE = 20;

export function ArticlesPage() {
  const { t, i18n } = useTranslation();
  const online = useOnlineStatus();
  const [searchParams, setSearchParams] = useSearchParams();
  const [search, setSearch] = useState(() => searchParams.get('q') || '');
  const [category, setCategory] = useState('');
  const [page, setPage] = useState(1);
  const debouncedSearch = useDebouncedValue(search);

  const { data: categories = [] } = useQuery({
    queryKey: queryKeys.categories(),
    queryFn: async () => {
      const { data } = await loadCategories();
      return data;
    },
  });

  // Support /articles?category=<slug|uuid> from landing "Explore topics"
  useEffect(() => {
    const raw = searchParams.get('category');
    if (!raw || !categories.length) return;
    const match = categories.find((c) => c.id === raw || c.slug === raw);
    if (!match) return;
    setCategory((prev) => {
      if (prev === match.id) return prev;
      setPage(1);
      return match.id;
    });
  }, [searchParams, categories]);

  const listParams = useMemo(() => {
    const params = { page: String(page) };
    if (debouncedSearch) params.search = debouncedSearch;
    if (category) params.category = category;
    return params;
  }, [page, debouncedSearch, category]);

  const { data, isLoading, isFetching, isError } = useQuery({
    queryKey: queryKeys.articles(listParams),
    queryFn: async () => {
      const result = await loadArticlesList(listParams);
      return { ...result.data, _source: result.source };
    },
  });

  const articles = data?.results ?? [];
  const totalCount = data?.count ?? 0;
  const fromCache = data?._source === 'cache';

  const categoryOptions = useMemo(
    () => [
      { id: '', name: t('common.all') },
      ...categories.map((cat) => ({ ...cat, name: localizedCategory(cat, i18n.language) })),
    ],
    [categories, t, i18n.language],
  );

  const activeCategory = useMemo(
    () => categories.find((c) => c.id === category),
    [categories, category],
  );
  const activeCategoryName = activeCategory
    ? localizedCategory(activeCategory, i18n.language)
    : '';

  const handleSearchChange = (value) => {
    setSearch(value);
    setPage(1);
  };

  const handleCategoryChange = (value) => {
    setCategory(value);
    setPage(1);
    const next = new URLSearchParams(searchParams);
    if (value) {
      const cat = categories.find((c) => c.id === value);
      next.set('category', cat?.slug || value);
    } else {
      next.delete('category');
    }
    setSearchParams(next, { replace: true });
  };

  return (
    <div className="page-shell">
      <PageHeader
        eyebrow={t('nav.learn')}
        title={t('articles.title')}
        subtitle={t('articles.subtitle')}
      />

      {!online && <Alert kind="warning">{t('offline.readingCached')}</Alert>}
      {fromCache && online && <Alert kind="warning">{t('offline.staleCache')}</Alert>}

      <div className="filter-bar flex flex-col gap-3 sm:flex-row sm:items-center">
        <input
          className="input sm:max-w-sm"
          placeholder={t('articles.searchPlaceholder')}
          value={search}
          onChange={(e) => handleSearchChange(e.target.value)}
        />
        <select
          className="input sm:max-w-xs"
          value={category}
          onChange={(e) => handleCategoryChange(e.target.value)}
        >
          {categoryOptions.map((c) => (
            <option key={c.id || 'all'} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      {activeCategory && (
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <span className="badge bg-brand-50 text-brand-800 dark:bg-brand-900/40 dark:text-brand-300">
            {t('articles.filteringBy', { category: activeCategoryName })}
          </span>
          <button
            type="button"
            className="text-sm font-semibold text-brand-700 hover:underline dark:text-brand-300"
            onClick={() => handleCategoryChange('')}
          >
            {t('articles.clearCategory')}
          </button>
        </div>
      )}

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      ) : isError && articles.length === 0 ? (
        <EmptyState title={t('articles.noArticles')}>{t('common.noResults')}</EmptyState>
      ) : articles.length === 0 ? (
        <EmptyState title={t('articles.noArticles')}>{t('common.noResults')}</EmptyState>
      ) : (
        <>
          {isFetching && !isLoading && (
            <p className="text-sm text-ink-700/55 dark:text-slate-400">{t('common.loading')}</p>
          )}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {articles.map((raw) => {
              const article = localizedArticle(raw, i18n.language);
              return (
                <Link
                  key={article.id}
                  to={`/articles/${article.id}`}
                  className="content-tile group"
                >
                  {article.featured_image_url && (
                    <img
                      src={article.featured_image_url}
                      alt=""
                      className="mb-4 h-36 w-full rounded-xl object-cover"
                    />
                  )}
                  <span className="badge mb-2 self-start bg-brand-50 text-brand-800 dark:bg-brand-900/40 dark:text-brand-300">
                    {article.category?.name}
                  </span>
                  <h3 className="font-display text-lg font-semibold text-ink-900 transition-colors group-hover:text-brand-700 dark:text-slate-100 dark:group-hover:text-brand-300">
                    {article.title}
                  </h3>
                  <p className="mt-2 line-clamp-3 flex-1 text-sm leading-relaxed text-ink-700/75 dark:text-slate-400">
                    {plainTextExcerpt(article.content)}
                  </p>
                  <div className="content-meta">
                    <span>{article.author_name}</span>
                    <span aria-hidden="true">·</span>
                    <span>
                      {readingTime(article.content)} {t('misc.minRead')}
                    </span>
                    <span aria-hidden="true">·</span>
                    <span>{formatDate(article.published_at)}</span>
                  </div>
                </Link>
              );
            })}
          </div>
          <Pagination
            page={page}
            totalCount={totalCount}
            pageSize={PAGE_SIZE}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  );
}
