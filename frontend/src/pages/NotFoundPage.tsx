// @ts-nocheck
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export function NotFoundPage() {
  const { t } = useTranslation();
  return (
    <div className="mx-auto flex max-w-md flex-col items-center px-4 py-16 text-center sm:py-20">
      <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-brand-50 text-brand-700 dark:bg-brand-950/50 dark:text-brand-300">
        <svg
          className="h-10 w-10"
          viewBox="0 0 200 200"
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <rect x="30" y="40" width="140" height="120" rx="16" />
          <path d="M70 90 Q100 70 130 90" />
          <circle cx="78" cy="78" r="8" fill="currentColor" stroke="none" />
          <circle cx="122" cy="78" r="8" fill="currentColor" stroke="none" />
          <line x1="80" y1="118" x2="120" y2="118" strokeWidth="10" />
        </svg>
      </div>
      <p className="font-display text-6xl font-semibold text-brand-700 dark:text-brand-400">404</p>
      <h1 className="mt-3 font-display text-2xl font-semibold text-ink-900 dark:text-slate-100">
        {t('errors.notFoundTitle')}
      </h1>
      <p className="mt-2 max-w-sm text-sm leading-relaxed text-ink-700/70 dark:text-slate-400">
        {t('errors.notFoundMessage')}
      </p>
      <Link to="/" className="btn-primary mt-8">
        {t('errors.goHome')}
      </Link>
    </div>
  );
}
