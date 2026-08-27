import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link, useSearchParams } from 'react-router-dom';
import { ClaimBadge, ClaimLegend, NEWS_CLAIM_TYPES, NEWS_TOPICS, TopicBadge } from '../components/ClaimBadge';
import { Pagination } from '../components/Pagination';
import { Alert, CardSkeleton, EmptyState, PageHeader } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import { formatDate } from '../lib/format';
import { localizedNews } from '../lib/localizedContent';
import { plainTextExcerpt } from '../lib/markdown';
import { queryKeys } from '../lib/queryKeys';
import { newsService } from '../lib/services';

const PAGE_SIZE = 20;

export function NewsPage() {
  const { t, i18n } = useTranslation();
  const { hasRole } = useAuth();
  const { isOrgContentManager } = useOrganization();
  const canManage = hasRole('admin', 'editor') || isOrgContentManager;
  const [searchParams, setSearchParams] = useSearchParams();
  const [page, setPage] = useState(1);

  const topic = searchParams.get('topic') || '';
  const claimType = searchParams.get('claim_type') || '';

  const listParams = useMemo(() => {
    const params: Record<string, string> = { page: String(page), status: 'published' };
    if (topic) params.topic = topic;
    if (claimType) params.claim_type = claimType;
    return params;
  }, [page, topic, claimType]);

  const { data, isLoading, isError } = useQuery({
    queryKey: queryKeys.news(listParams),
    queryFn: async () => {
      const { data: res } = await newsService.list(listParams);
      return res;
    },
  });

  const items = (data?.results ?? []).map((item) => localizedNews(item, i18n.language));
  const totalCount = data?.count ?? 0;

  const setFilter = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams);
    if (value) next.set(key, value);
    else next.delete(key);
    setSearchParams(next, { replace: true });
    setPage(1);
  };

  return (
    <div className="page-shell">
      <PageHeader
        eyebrow={t('nav.learn')}
        title={t('news.title')}
        subtitle={t('news.subtitle')}
      />

      {canManage && (
        <div className="mb-6 flex justify-end">
          <Link to="/news/manage" className="btn-secondary text-sm">
            {t('news.manage')}
          </Link>
        </div>
      )}

      <ClaimLegend className="mb-6" />

      <div className="filter-bar mb-6 flex flex-col gap-3 sm:flex-row sm:items-center">
        <select
          className="input sm:max-w-xs"
          value={topic}
          aria-label={t('news.filterTopic')}
          onChange={(e) => setFilter('topic', e.target.value)}
        >
          <option value="">{t('news.allTopics')}</option>
          {NEWS_TOPICS.map((value) => (
            <option key={value} value={value}>
              {t(`news.topics.${value}`)}
            </option>
          ))}
        </select>
        <select
          className="input sm:max-w-xs"
          value={claimType}
          aria-label={t('news.filterClaim')}
          onChange={(e) => setFilter('claim_type', e.target.value)}
        >
          <option value="">{t('news.allClaims')}</option>
          {NEWS_CLAIM_TYPES.map((value) => (
            <option key={value} value={value}>
              {t(`news.claims.${value}`)}
            </option>
          ))}
        </select>
      </div>

      {isError && <Alert>{t('common.noResults')}</Alert>}
      {isLoading && <CardSkeleton />}
      {!isLoading && items.length === 0 && (
        <EmptyState title={t('news.empty')} />
      )}

      <div className="grid gap-4">
        {items.map((item) => (
          <Link
            key={item.id}
            to={`/news/${item.id}`}
            className="card block p-5 transition hover:-translate-y-0.5 hover:shadow-lift"
          >
            <div className="flex flex-wrap items-center gap-2">
              <TopicBadge topic={item.topic} />
              <ClaimBadge claimType={item.claim_type} />
            </div>
            <h2 className="mt-3 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">
              {item.title}
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-ink-700/75 dark:text-slate-400">
              {plainTextExcerpt(item.body)}
            </p>
            {item.published_at && (
              <p className="mt-3 text-xs text-ink-700/50 dark:text-slate-500">
                {formatDate(item.published_at)}
              </p>
            )}
          </Link>
        ))}
      </div>

      {totalCount > PAGE_SIZE && (
        <Pagination
          page={page}
          pageSize={PAGE_SIZE}
          totalCount={totalCount}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}
