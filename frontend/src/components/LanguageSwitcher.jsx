import { useTranslation } from "react-i18next";
import toast from "react-hot-toast";
import { useAuth } from "../context/AuthContext";
import { extractError } from "../lib/api";
import { userService } from "../lib/services";
import { normalizeLanguage } from "../i18n/languages";

function LanguageSwitcher() {
  const { i18n, t } = useTranslation();
  const { user, refreshUser } = useAuth();
  const current = normalizeLanguage(i18n.language);

  const toggle = async () => {
    const next = current === "ar" ? "en" : "ar";
    await i18n.changeLanguage(next);
    if (!user) return;
    try {
      await userService.updateProfile({ preferred_language: next });
      await refreshUser();
    } catch (err) {
      toast.error(extractError(err));
    }
  };

  return (
    <button
      type="button"
      onClick={toggle}
      className="rounded-xl border border-ink-200 px-2 py-2 text-xs font-medium text-ink-700 hover:bg-ink-100/70 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800 sm:px-3 sm:py-1.5 sm:text-sm"
      aria-label={t("nav.switchLanguage")}
    >
      {current === "ar" ? "EN" : "عربي"}
    </button>
  );
}

export { LanguageSwitcher };
