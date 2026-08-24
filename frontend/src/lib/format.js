import i18n from '../i18n';

function formatDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString(i18n.language === 'ar' ? 'ar-EG' : 'en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function formatDateTime(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleString(i18n.language === 'ar' ? 'ar-EG' : 'en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

function readingTime(content) {
  if (!content) return 1;
  const text = content.replace(/<[^>]+>/g, ' ');
  const words = text.trim().split(/\s+/).filter(Boolean).length;
  return Math.max(1, Math.ceil(words / 200));
}

export { formatDate, formatDateTime, readingTime };
