/**
 * Detect YouTube / Vimeo URLs and return an embeddable iframe src.
 * Returns null for direct file URLs (use native <video>).
 */
export function getEmbedInfo(url, { lang = 'en' } = {}) {
  if (!url || typeof url !== 'string') return null;
  const trimmed = url.trim();
  const captionsLang = lang === 'ar' ? 'ar' : 'en';

  const yt =
    trimmed.match(
      /(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([A-Za-z0-9_-]{6,})/,
    ) || trimmed.match(/youtube\.com\/watch\?.*?v=([A-Za-z0-9_-]{6,})/);
  if (yt?.[1]) {
    return {
      provider: 'youtube',
      src: `https://www.youtube.com/embed/${yt[1]}?cc_load_policy=1&cc_lang_pref=${captionsLang}`,
    };
  }

  const vimeo = trimmed.match(/vimeo\.com\/(?:video\/)?(\d+)/);
  if (vimeo?.[1]) {
    return {
      provider: 'vimeo',
      src: `https://player.vimeo.com/video/${vimeo[1]}?texttrack=${captionsLang}`,
    };
  }

  return null;
}
