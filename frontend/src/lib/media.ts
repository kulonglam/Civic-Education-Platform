const API_ORIGIN = (
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1'
).replace(/\/api(\/v1)?\/?$/, '');

/** Turn relative /media/... paths into absolute API URLs for downloads and images. */
export function resolveMediaUrl(url?: string | null) {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  if (url.startsWith('/')) return `${API_ORIGIN}${url}`;
  return url;
}
