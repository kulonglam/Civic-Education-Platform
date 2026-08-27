import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Alert } from "./ui";
function QuotaBanner() {
  const {
    t
  } = useTranslation();
  const [message, setMessage] = useState("");
  useEffect(() => {
    const handler = (event: Event) => {
      const detail = (event as CustomEvent<string>).detail;
      setMessage(detail || t("saas.quotaExceeded"));
    };
    window.addEventListener("cep:quota-exceeded", handler);
    return () => window.removeEventListener("cep:quota-exceeded", handler);
  }, [t]);
  if (!message) return null;
  return <div className="border-b border-amber-200 bg-amber-50 px-4 py-2 dark:border-amber-900/40 dark:bg-amber-950/40"><div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-2"><Alert kind="warning">{message}</Alert><Link to="/billing" className="text-sm font-medium text-brand-700 hover:underline dark:text-brand-400">{t("saas.upgradePlan")}</Link></div></div>;
}
export { QuotaBanner };