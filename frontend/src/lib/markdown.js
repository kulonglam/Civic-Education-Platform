import DOMPurify from 'dompurify';
import { marked } from 'marked';

marked.setOptions({ breaks: true, gfm: true });

const SANITIZE_OPTIONS = {
  ALLOWED_TAGS: [
    'p', 'br', 'strong', 'em', 'b', 'i', 'u', 'ul', 'ol', 'li', 'a',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'code', 'pre', 'hr',
  ],
  ALLOWED_ATTR: ['href', 'title', 'rel', 'target', 'class'],
};

export function renderMarkdown(text) {
  if (!text) return '';
  const html = marked.parse(text);
  return DOMPurify.sanitize(html, SANITIZE_OPTIONS);
}

/** Plain-text preview for list cards (strips markdown syntax). */
export function plainTextExcerpt(text, maxLength = 160) {
  if (!text) return '';
  const stripped = text
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/`[^`]*`/g, ' ')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/(\*\*|__|\*|_|~~)/g, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  if (stripped.length <= maxLength) return stripped;
  return `${stripped.slice(0, maxLength).trimEnd()}…`;
}
