/** Supported UI/content languages — English and Arabic only. */
export const SUPPORTED_LANGUAGES = ["en", "ar"];
export const DEFAULT_LANGUAGE = "en";
export const RTL_LANGUAGES = ["ar"];

/** Map any stored/browser language code to ``en`` or ``ar``. */
export function normalizeLanguage(lang) {
  if (!lang) return DEFAULT_LANGUAGE;
  if (lang === "ar" || String(lang).startsWith("ar")) return "ar";
  return DEFAULT_LANGUAGE;
}

/** Clear invalid values left in localStorage from older builds. */
export function sanitizeStoredLanguage(storageKey = "cep_lang") {
  const stored = localStorage.getItem(storageKey);
  if (!stored) return;
  const normalized = normalizeLanguage(stored);
  if (normalized !== stored) {
    localStorage.setItem(storageKey, normalized);
  }
}
