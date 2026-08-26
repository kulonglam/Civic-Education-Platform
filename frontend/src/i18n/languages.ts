/** Supported UI/content languages — English and Arabic only. */
export const SUPPORTED_LANGUAGES = ['en', 'ar'] as const;
export const DEFAULT_LANGUAGE = 'en';
export const RTL_LANGUAGES = ['ar'] as const;

export type UiLanguage = (typeof SUPPORTED_LANGUAGES)[number];

/** Map any stored/browser language code to ``en`` or ``ar``. */
export function normalizeLanguage(lang?: string | null): UiLanguage {
  if (!lang) return DEFAULT_LANGUAGE;
  if (lang === 'ar' || String(lang).startsWith('ar')) return 'ar';
  return DEFAULT_LANGUAGE;
}

/** Clear invalid values left in localStorage from older builds. */
export function sanitizeStoredLanguage(storageKey = 'cep_lang'): void {
  if (typeof localStorage === 'undefined') return;
  const stored = localStorage.getItem(storageKey);
  if (!stored) return;
  const normalized = normalizeLanguage(stored);
  if (normalized !== stored) {
    localStorage.setItem(storageKey, normalized);
  }
}
