import { resolveMediaUrl } from '../lib/media';
import { getEmbedInfo } from '../lib/mediaEmbed';

/**
 * Plays audio or video from a MediaAsset-like object or raw URL.
 * YouTube/Vimeo URLs render as iframes; other URLs use native media elements.
 */
export function MediaPlayer({
  mediaType = 'video',
  url,
  captionsUrl = '',
  title = '',
  className = '',
  onEnded,
}) {
  const playback = resolveMediaUrl(url || '');
  const captions = resolveMediaUrl(captionsUrl || '');
  if (!playback) return null;

  const track = captions ? (
    <track kind="captions" src={captions} srcLang="en" label="Captions" default />
  ) : null;

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
        >
          {track}
        </audio>
      </div>
    );
  }

  const embed = getEmbedInfo(playback);
  if (embed) {
    return (
      <div className={`aspect-video overflow-hidden rounded-xl bg-ink-950 ${className}`}>
        <iframe
          title={title || 'Video'}
          src={embed.src}
          className="h-full w-full"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          loading="lazy"
          referrerPolicy="strict-origin-when-cross-origin"
        />
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
      >
        {track}
      </video>
    </div>
  );
}
