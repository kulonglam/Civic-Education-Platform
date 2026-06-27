import { useTranslation } from "react-i18next";
import { normalizeLanguage } from "../i18n/languages";

function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const current = normalizeLanguage(i18n.language);

  const toggle = () => {
    i18n.changeLanguage(current === "ar" ? "en" : "ar");
  };

  return (
    <button
      onClick={toggle}
      className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700"
      aria-label="Switch language"
    >
      {current === "ar" ? "EN" : "عربي"}
    </button>
  );
}

export { LanguageSwitcher };
