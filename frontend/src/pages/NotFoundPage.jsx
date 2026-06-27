import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export function NotFoundPage() {
  const { t } = useTranslation();
  return (
    <div className="mx-auto flex max-w-md flex-col items-center py-20 text-center">
      <svg
        className="mb-6 h-40 w-40 text-gray-200 dark:text-slate-700"
        viewBox="0 0 200 200"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <rect x="30" y="40" width="140" height="120" rx="8" />
        <path d="M70 90 Q100 70 130 90" />
        <circle cx="78" cy="78" r="6" fill="currentColor" stroke="none" />
        <circle cx="122" cy="78" r="6" fill="currentColor" stroke="none" />
        <line x1="80" y1="110" x2="120" y2="110" strokeWidth="3" />
      </svg>
      <p className="text-7xl font-extrabold text-brand-600 dark:text-brand-400">404</p>
      <h1 className="mt-3 text-2xl font-bold text-gray-900 dark:text-slate-100">
        {t('errors.notFoundTitle')}
      </h1>
      <p className="mt-2 text-gray-500 dark:text-slate-400">{t('errors.notFoundMessage')}</p>
      <Link to="/" className="btn-primary mt-8">
        {t('errors.goHome')}
      </Link>
    </div>
  );
}
