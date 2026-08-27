import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export function GuestSaveCta({ className = '' }) {
  const { t } = useTranslation();
  const location = useLocation();
  const from = location.pathname + location.search;

  return (
    <div
      className={`rounded-xl border border-brand-200 bg-brand-50 px-4 py-3.5 text-sm leading-relaxed text-brand-800 shadow-soft dark:border-brand-900 dark:bg-brand-950/40 dark:text-brand-200 ${className}`}
    >
      <p>{t('guest.saveProgress')}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        <Link to="/register" state={{ from }} className="btn-primary text-sm">
          {t('guest.createAccount')}
        </Link>
        <Link to="/login" state={{ from }} className="btn-secondary text-sm">
          {t('guest.signIn')}
        </Link>
      </div>
    </div>
  );
}
