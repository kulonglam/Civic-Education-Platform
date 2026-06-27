import { useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
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
  const [search, setSearch] = useState('');
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

  const handleSearchChange = (value) => {
    setSearch(value);
    setPage(1);
  };

  const handleCategoryChange = (value) => {
    setCategory(value);
    setPage(1);
  };

  return (
    <div>
      <PageHeader title={t('articles.title')} />

      {!online && (
        <div className="mb-4">
          <Alert kind="warning">{t('offline.readingCached')}</Alert>
        </div>
      )}
      {fromCache && online && (
        <div className="mb-4">
          <Alert kind="warning">{t('offline.staleCache')}</Alert>
        </div>
      )}

      <div className="mb-6 flex flex-col gap-3 sm:flex-row">
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

      {isLoading ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      ) : isError && articles.length === 0 ? (
        <EmptyState>{t('articles.noArticles')}</EmptyState>
      ) : articles.length === 0 ? (
        <EmptyState>{t('articles.noArticles')}</EmptyState>
      ) : (
        <>
          {isFetching && !isLoading && (
            <p className="mb-4 text-sm text-gray-500 dark:text-slate-400">{t('common.loading')}</p>
          )}
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {articles.map((raw) => {
              const article = localizedArticle(raw, i18n.language);
              return (
              <Link
                key={article.id}
                to={`/articles/${article.id}`}
                className="card group flex flex-col transition-shadow hover:shadow-md dark:hover:border-slate-600"
              >
                {article.featured_image_url && (
                  <img
                    src={article.featured_image_url}
                    alt={article.title}
                    className="mb-4 h-40 w-full rounded-lg object-cover"
                  />
                )}
                <span className="badge mb-2 self-start bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
                  {article.category?.name}
                </span>
                <h3 className="text-lg font-semibold text-gray-900 group-hover:text-brand-700 dark:text-slate-100 dark:group-hover:text-brand-300">
                  {article.title}
                </h3>
                <p className="mt-2 line-clamp-3 flex-1 text-sm text-gray-600 dark:text-slate-400">
                  {plainTextExcerpt(article.content)}
                </p>
                <div className="mt-4 flex items-center justify-between text-xs text-gray-400 dark:text-slate-500">
                  <span>{article.author_name}</span>
                  <span className="flex items-center gap-2">
                    <span>{readingTime(article.content)} {t('misc.minRead')}</span>
                    <span>·</span>
                    <span>{formatDate(article.published_at)}</span>
                  </span>
                </div>
              </Link>
            );})}
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
