import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Alert, EmptyState, PageHeader, Spinner } from '../components/ui';
import { queryKeys } from '../lib/queryKeys';
import { mediaService } from '../lib/services';
import { formatDate } from '../lib/format';

export function MediaPage() {
  const { t } = useTranslation();
  const [mediaType, setMediaType] = useState('');

  const params = useMemo(() => {
    const p = { page_size: '50' };
    if (mediaType) p.media_type = mediaType;
    return p;
  }, [mediaType]);

  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.media(params),
    queryFn: async () => {
      const { data: res } = await mediaService.list(params);
      return res.results ?? res;
    },
  });

  const items = data ?? [];

  return (
    <div className="page-shell">
      <PageHeader
        eyebrow={t('nav.learn')}
        title={t('media.title')}
        subtitle={t('media.subtitle')}
      />
      <div className="filter-bar flex flex-wrap gap-2">
        {[
          { value: '', label: t('common.all') },
          { value: 'audio', label: t('media.typeAudio') },
          { value: 'video', label: t('media.typeVideo') },
        ].map((opt) => (
          <button
            key={opt.value || 'all'}
            type="button"
            className={
              mediaType === opt.value
                ? 'btn-primary text-sm'
                : 'btn-secondary text-sm'
            }
            onClick={() => setMediaType(opt.value)}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {isLoading && <Spinner />}
      {error && <Alert>{t('common.noResults')}</Alert>}
      {!isLoading && !error && items.length === 0 && (
        <EmptyState title={t('media.empty')}>{t('common.noResults')}</EmptyState>
      )}
      {!isLoading && items.length > 0 && (
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <li key={item.id}>
              <Link to={`/media/${item.id}`} className="content-tile group h-full">
                <span className="badge mb-2 self-start bg-brand-50 text-brand-700 dark:bg-brand-950/50 dark:text-brand-300">
                  {item.media_type === 'audio'
                    ? t('media.typeAudio')
                    : t('media.typeVideo')}
                </span>
                <h2 className="font-display text-lg font-semibold text-ink-900 transition-colors group-hover:text-brand-700 dark:text-slate-100 dark:group-hover:text-brand-300">
                  {item.title}
                </h2>
                {item.description && (
                  <p className="mt-2 line-clamp-2 flex-1 text-sm leading-relaxed text-ink-700/75 dark:text-slate-400">
                    {item.description}
                  </p>
                )}
                {item.published_at && (
                  <p className="content-meta">{formatDate(item.published_at)}</p>
                )}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
