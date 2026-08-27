import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";
import ar from "./ar.json";
import en from "./en.json";
import {
  DEFAULT_LANGUAGE,
  RTL_LANGUAGES,
  SUPPORTED_LANGUAGES,
  normalizeLanguage,
  sanitizeStoredLanguage,
} from "./languages";

sanitizeStoredLanguage();

i18n.use(LanguageDetector).use(initReactI18next).init({
  resources: {
    en: { translation: en },
    ar: { translation: ar },
  },
  fallbackLng: DEFAULT_LANGUAGE,
  supportedLngs: SUPPORTED_LANGUAGES,
  nonExplicitSupportedLngs: false,
  load: "languageOnly",
  detection: {
    order: ["localStorage", "navigator"],
    lookupLocalStorage: "cep_lang",
    caches: ["localStorage"],
  },
  interpolation: { escapeValue: false },
});

function applyDirection(lng) {
  const lang = normalizeLanguage(lng);
  const dir = RTL_LANGUAGES.includes(lang) ? "rtl" : "ltr";
  document.documentElement.dir = dir;
  document.documentElement.lang = lang;
}

const initial = normalizeLanguage(i18n.language);
if (initial !== i18n.language) {
  i18n.changeLanguage(initial);
} else {
  applyDirection(initial);
}

i18n.on("languageChanged", (lng) => {
  const lang = normalizeLanguage(lng);
  if (lang !== lng) {
    i18n.changeLanguage(lang);
    return;
  }
  applyDirection(lang);
});

export { RTL_LANGUAGES, SUPPORTED_LANGUAGES, normalizeLanguage };
export default i18n;
