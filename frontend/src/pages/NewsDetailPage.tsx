// @ts-nocheck
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { Breadcrumb } from '../components/Breadcrumb';
import { ClaimBadge, TopicBadge, claimAlertKind } from '../components/ClaimBadge';
import { Alert, Spinner } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import { formatDate } from '../lib/format';
import { localizedNews } from '../lib/localizedContent';
import { renderMarkdown, toPlainText } from '../lib/markdown';
import { queryKeys } from '../lib/queryKeys';
import { newsService } from '../lib/services';
import { ReadAloudButton } from '../components/ReadAloudButton';

export function NewsDetailPage() {
  const { t, i18n } = useTranslation();
  const { id } = useParams();
  const { hasRole } = useAuth();
  const { isOrgContentManager } = useOrganization();
  const canEdit = hasRole('admin', 'editor') || isOrgContentManager;

  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.newsItem(id),
    enabled: !!id,
    queryFn: async () => {
      const { data: res } = await newsService.get(id);
      return res;
    },
  });

  if (isLoading) return <Spinner />;
  if (error || !data) return <Alert>{t('common.noResults')}</Alert>;

  const item = localizedNews(data, i18n.language);
  const alertKind = claimAlertKind(item.claim_type);

  return (
    <div className="page-shell">
      <Breadcrumb
        items={[
          { to: '/news', label: t('news.title') },
          { label: item.title },
        ]}
      />

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <TopicBadge topic={item.topic} />
        <ClaimBadge claimType={item.claim_type} />
        {canEdit && (
          <Link to={`/news/${item.id}/edit`} className="btn-secondary ms-auto text-sm">
            {t('common.edit')}
          </Link>
        )}
        <ReadAloudButton text={`${item.title}. ${toPlainText(item.body)}`} />
      </div>

      <h1 className="mt-4 font-display text-3xl font-semibold text-ink-900 dark:text-slate-100">
        {item.title}
      </h1>
      {item.published_at && (
        <p className="mt-2 text-sm text-ink-700/60 dark:text-slate-400">
          {formatDate(item.published_at)}
        </p>
      )}

      <div className="mt-6">
        <Alert kind={alertKind}>
          <p className="font-semibold">{t(`news.claims.${item.claim_type}`)}</p>
          <p className="mt-1">{t(`news.detailNotice.${item.claim_type}`)}</p>
          {item.claim_type === 'verified_fact' && item.source_name && (
            <p className="mt-2">
              {t('news.source')}:{' '}
              {item.source_url ? (
                <a
                  href={item.source_url}
                  className="font-medium underline"
                  target="_blank"
                  rel="noreferrer"
                >
                  {item.source_name}
                </a>
              ) : (
                <span className="font-medium">{item.source_name}</span>
              )}
            </p>
          )}
        </Alert>
      </div>

      <div
        className="prose mt-8 max-w-none dark:prose-invert"
        dangerouslySetInnerHTML={{ __html: renderMarkdown(item.body) }}
      />
    </div>
  );
}
