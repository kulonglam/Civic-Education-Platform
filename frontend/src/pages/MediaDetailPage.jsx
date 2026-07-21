import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { MediaPlayer } from '../components/MediaPlayer';
import { Alert, Spinner } from '../components/ui';
import { Breadcrumb } from '../components/Breadcrumb';
import { useAuth } from '../context/AuthContext';
import { queryKeys } from '../lib/queryKeys';
import { mediaService } from '../lib/services';
import { formatDate } from '../lib/format';

export function MediaDetailPage() {
  const { t } = useTranslation();
  const { id } = useParams();
  const { hasRole } = useAuth();
  const canEdit = hasRole('admin', 'editor');

  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.mediaItem(id),
    enabled: !!id,
    queryFn: async () => {
      const { data: res } = await mediaService.get(id);
      return res;
    },
  });

  if (isLoading) return <Spinner />;
  if (error || !data) return <Alert>{t('common.noResults')}</Alert>;

  const playback = data.playback_url || data.external_url || data.file_url;

  return (
    <article className="mx-auto max-w-3xl">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <Breadcrumb
          items={[
            { to: '/media', label: t('media.title') },
            { label: data.title },
          ]}
        />
        {canEdit && (
          <Link to={`/media/${data.id}/edit`} className="btn-secondary text-sm">
            {t('common.edit')}
          </Link>
        )}
      </div>

      <span className="badge mb-3 bg-brand-50 text-brand-700">
        {data.media_type === 'audio' ? t('media.typeAudio') : t('media.typeVideo')}
      </span>
      <h1 className="font-display text-3xl font-semibold text-ink-900 dark:text-slate-50">
        {data.title}
      </h1>
      <p className="mt-2 text-sm text-ink-700/70 dark:text-slate-400">
        {data.author_name ? `${data.author_name} · ` : ''}
        {data.published_at ? formatDate(data.published_at) : null}
      </p>

      <div className="mt-6">
        <MediaPlayer
          mediaType={data.media_type}
          url={playback}
          title={data.title}
        />
      </div>

      {data.description && (
        <p className="mt-6 text-base leading-relaxed text-ink-800 dark:text-slate-300">
          {data.description}
        </p>
      )}
    </article>
  );
}
