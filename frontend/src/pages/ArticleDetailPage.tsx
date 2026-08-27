import { useQuery } from '@tanstack/react-query';
import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { MediaPlayer } from '../components/MediaPlayer';
import { Alert, Spinner } from '../components/ui';
import { Breadcrumb } from '../components/Breadcrumb';
import { FileText } from '../components/Icons';
import { queryKeys } from '../lib/queryKeys';
import { loadArticle } from '../lib/offline/articles';
import { formatDate, readingTime } from '../lib/format';
import { localizedArticle } from '../lib/localizedContent';
import { renderMarkdown, toPlainText } from '../lib/markdown';
import { resolveMediaUrl } from '../lib/media';
import { articleService } from '../lib/services';
import { BookmarkButton } from '../components/BookmarkButton';
import { GuestSaveCta } from '../components/GuestSaveCta';
import { ReadAloudButton } from '../components/ReadAloudButton';
import { WhatsAppShareButton } from '../components/WhatsAppShareButton';

export function ArticleDetailPage() {
  const { t, i18n } = useTranslation();
  const { user, hasRole } = useAuth();
  const { id } = useParams();
  const [readProgress, setReadProgress] = useState(0);
  const progressSentRef = useRef({ lastPct: 0, completed: false });

  useEffect(() => {
    const update = () => {
      const el = document.documentElement;
      const scrollable = el.scrollHeight - el.clientHeight;
      setReadProgress(scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0);
    };
    window.addEventListener('scroll', update, { passive: true });
    return () => window.removeEventListener('scroll', update);
  }, []);

  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.article(id),
    enabled: !!id,
    queryFn: async () => loadArticle(id),
  });

  const isCached = data?.source === 'cache';

  useEffect(() => {
    if (!user || !id || isCached) return undefined;

    const pct = Math.round(readProgress);
    const shouldComplete = pct >= 90;
    const throttleMs = shouldComplete ? 0 : 4000;
    const delta = Math.abs(pct - progressSentRef.current.lastPct);
    if (!shouldComplete && delta < 10 && progressSentRef.current.lastPct > 0) {
      return undefined;
    }
    if (shouldComplete && progressSentRef.current.completed) {
      return undefined;
    }

    const timer = window.setTimeout(() => {
      articleService
        .recordProgress(id, {
          progress_percent: pct,
          completed: shouldComplete,
        })
        .then(() => {
          progressSentRef.current.lastPct = pct;
          if (shouldComplete) progressSentRef.current.completed = true;
        })
        .catch(() => {});
    }, throttleMs);

    return () => window.clearTimeout(timer);
  }, [user, id, readProgress, isCached]);

  if (isLoading) return <Spinner />;
  if (error || !data?.data) return <Alert>{t('common.noResults')}</Alert>;

  const article = localizedArticle(data.data, i18n.language);
  const fromCache = data.source === 'cache';
  const canEdit = hasRole('admin', 'editor');

  const mins = readingTime(article.content);

  return (
    <article className="reading-shell">
      {/* Reading progress bar fixed at top of viewport */}
      <div
        className="fixed left-0 top-0 z-50 h-0.5 bg-brand-500 transition-all duration-100"
        style={{ width: `${readProgress}%` }}
        aria-hidden="true"
      />
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <Breadcrumb items={[
          { to: '/articles', label: t('articles.title') },
          { label: article.title },
        ]} />
        <div className="flex flex-wrap items-center gap-2">
          <ReadAloudButton text={`${article.title}. ${toPlainText(article.content)}`} />
          <WhatsAppShareButton title={article.title} path={`/articles/${article.id}`} />
          <BookmarkButton kind="article" id={article.id} bookmarked={article.is_bookmarked} />
          {canEdit && (
            <Link to={`/articles/${article.id}/edit`} className="btn-secondary text-sm">
              {t('common.edit')}
            </Link>
          )}
        </div>
      </div>
      {!user && <GuestSaveCta className="mb-6" />}
      {fromCache && (
        <div className="mb-4">
          <Alert kind="warning">{t('offline.cachedArticle')}</Alert>
        </div>
      )}
      {article.featured_image_url && (
        <img
          src={resolveMediaUrl(article.featured_image_url)}
          alt={article.title}
          className="mb-8 h-64 w-full rounded-2xl object-cover shadow-soft sm:h-72"
        />
      )}
      <span className="badge mb-4 bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
        {article.category?.name}
      </span>
      <h1 className="font-display text-3xl font-semibold leading-tight text-ink-900 dark:text-slate-50 sm:text-4xl">
        {article.title}
      </h1>
      <div className="content-meta mt-4 text-sm">
        <span>{t('articles.by')} {article.author_name}</span>
        <span aria-hidden="true">·</span>
        <span>{formatDate(article.published_at)}</span>
        <span aria-hidden="true">·</span>
        <span>{mins} {t('misc.minRead')}</span>
      </div>
      {article.tags?.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {article.tags.map((tag) => (
            <span key={tag} className="badge bg-ink-100 text-ink-700 dark:bg-slate-700 dark:text-slate-300">
              #{tag}
            </span>
          ))}
        </div>
      )}
      {article.attachment_url && (
        <a
          href={resolveMediaUrl(article.attachment_url)}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-6 inline-flex items-center gap-2 rounded-xl border border-brand-200 bg-brand-50 px-4 py-3 text-sm font-medium text-brand-800 transition-colors hover:bg-brand-100 dark:border-brand-900/50 dark:bg-brand-950/40 dark:text-brand-200 dark:hover:bg-brand-900/40"
        >
          <FileText className="h-5 w-5 shrink-0" />
          <span>
            {t('articles.downloadAttachment')}
            {article.attachment_name ? `: ${article.attachment_name}` : ''}
            {article.is_controlled_document && article.attachment_version
              ? ` (${article.document_label || t('articles.controlledDocument')} · ${article.attachment_version})`
              : ''}
          </span>
        </a>
      )}
      {article.video_media?.playback_url || article.video_media?.external_url || article.video_media?.file_url ? (
        <div className="mt-8">
          <h2 className="mb-3 font-display text-lg font-semibold text-ink-900 dark:text-slate-100">
            {t('media.typeVideo')}
          </h2>
          <MediaPlayer
            mediaType="video"
            url={
              article.video_media.playback_url ||
              article.video_media.external_url ||
              article.video_media.file_url
            }
            captionsUrl={article.video_media.captions_url}
            title={article.video_media.title || article.title}
          />
        </div>
      ) : null}
      {article.audio_media?.playback_url || article.audio_media?.external_url || article.audio_media?.file_url ? (
        <div className="mt-8">
          <h2 className="mb-3 font-display text-lg font-semibold text-ink-900 dark:text-slate-100">
            {t('media.typeAudio')}
          </h2>
          <MediaPlayer
            mediaType="audio"
            url={
              article.audio_media.playback_url ||
              article.audio_media.external_url ||
              article.audio_media.file_url
            }
            captionsUrl={article.audio_media.captions_url}
            title={article.audio_media.title || article.title}
          />
        </div>
      ) : null}
      {user && (
        <Link
          to={`/tutor?article=${article.id}`}
          className="btn-secondary mt-8 inline-block"
        >
          {t('tutor.askAboutArticle')}
        </Link>
      )}
      <div
        className="reading-prose prose max-w-none dark:prose-invert"
        dangerouslySetInnerHTML={{ __html: renderMarkdown(article.content) }}
      />
    </article>
  );
}
