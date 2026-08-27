import { useTranslation } from 'react-i18next';
import { resolveMediaUrl } from '../lib/media';
import { getEmbedInfo } from '../lib/mediaEmbed';

/**
 * Plays audio or video from a MediaAsset-like object or raw URL.
 * YouTube/Vimeo URLs render as iframes with captions requested;
 * other URLs use native media elements and an optional WebVTT track.
 */
export function MediaPlayer({
  mediaType = 'video',
  url,
  captionsUrl = '',
  title = '',
  className = '',
  onEnded,
}) {
  const { t, i18n } = useTranslation();
  const playback = resolveMediaUrl(url || '');
  const captions = resolveMediaUrl(captionsUrl || '');
  const captionsLang = i18n.language === 'ar' ? 'ar' : 'en';
  if (!playback) return null;

  const track = captions ? (
    <track
      kind="captions"
      src={captions}
      srcLang={captionsLang}
      label={t('a11y.captions')}
      default={true}
    />
  ) : null;

  const captionStatus = captions
    ? t('a11y.captionsAvailable')
    : t('a11y.captionsMissing');

  if (mediaType === 'audio') {
    return (
      <div className={className}>
        <audio
          className="w-full"
          controls
          preload="metadata"
          src={playback}
          title={title || undefined}
          onEnded={onEnded}
          crossOrigin={captions ? 'anonymous' : undefined}
        >
          {track}
        </audio>
        <p className="mt-2 text-xs text-ink-700/70 dark:text-slate-400">{captionStatus}</p>
      </div>
    );
  }

  const embed = getEmbedInfo(playback, { lang: captionsLang });
  if (embed) {
    return (
      <div className={className}>
        <div className="aspect-video overflow-hidden rounded-xl bg-ink-950">
          <iframe
            title={title || t('media.typeVideo')}
            src={embed.src}
            className="h-full w-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            loading="lazy"
            referrerPolicy="strict-origin-when-cross-origin"
          />
        </div>
        <p className="mt-2 text-xs text-ink-700/70 dark:text-slate-400">
          {captions ? t('a11y.captionsAvailable') : t('a11y.captionsOnPlayer')}
        </p>
      </div>
    );
  }

  return (
    <div className={className}>
      <video
        className="w-full rounded-xl bg-ink-950"
        controls
        playsInline
        preload="metadata"
        src={playback}
        title={title || undefined}
        onEnded={onEnded}
        crossOrigin={captions ? 'anonymous' : undefined}
      >
        {track}
      </video>
      <p className="mt-2 text-xs text-ink-700/70 dark:text-slate-400">{captionStatus}</p>
    </div>
  );
}
