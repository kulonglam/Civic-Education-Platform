const STORAGE_KEY = 'cep_a11y';

export const FONT_SCALES = [
  { id: 'md', percent: 100 },
  { id: 'lg', percent: 125 },
  { id: 'xl', percent: 150 },
  { id: 'xxl', percent: 175 },
];

export const DEFAULT_A11Y = {
  fontScale: 'md',
  highContrast: false,
};

export function readA11ySettings() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ...DEFAULT_A11Y };
    const parsed = JSON.parse(raw);
    const fontScale = FONT_SCALES.some((item) => item.id === parsed.fontScale)
      ? parsed.fontScale
      : DEFAULT_A11Y.fontScale;
    return {
      fontScale,
      highContrast: Boolean(parsed.highContrast),
    };
  } catch {
    return { ...DEFAULT_A11Y };
  }
}

export function writeA11ySettings(settings) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
}

export function applyA11ySettings(settings) {
  const root = document.documentElement;
  if (!root) return;
  if (!settings.fontScale || settings.fontScale === 'md') {
    delete root.dataset.fontSize;
  } else {
    root.dataset.fontSize = settings.fontScale;
  }
  if (settings.highContrast) {
    root.dataset.contrast = 'high';
  } else {
    delete root.dataset.contrast;
  }
}

export function parseVtt(text) {
  if (!text) return '';
  return text
    .replace(/^\uFEFF/, '')
    .split(/\r?\n/)
    .filter((line) => {
      const trimmed = line.trim();
      if (!trimmed) return false;
      if (trimmed === 'WEBVTT' || trimmed.startsWith('NOTE')) return false;
      if (/^\d+$/.test(trimmed)) return false;
      if (/-->/.test(trimmed)) return false;
      return true;
    })
    .join(' ')
    .replace(/\s+/g, ' ')
    .trim();
}

export function pagePlainText(root = document.getElementById('main-content')) {
  if (!root) return '';
  const clone = root.cloneNode(true);
  clone.querySelectorAll('.sr-only, [aria-hidden="true"], script, style, noscript').forEach((el) => el.remove());
  return (clone.innerText || '').replace(/\s+/g, ' ').trim();
}
