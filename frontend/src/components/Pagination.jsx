import { useTranslation } from 'react-i18next';

export function Pagination({ page, totalCount, pageSize = 20, onPageChange }) {
  const { t } = useTranslation();
  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  if (totalCount <= pageSize) return null;

  return (
    <nav
      className="mt-8 flex flex-wrap items-center justify-center gap-3"
      aria-label={t('pagination.label')}
    >
      <button
        type="button"
        className="btn-secondary"
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
      >
        {t('pagination.previous')}
      </button>
      <span className="text-sm text-ink-700/80 dark:text-slate-400" aria-current="page">
        {t('pagination.pageOf', { page, total: totalPages })}
      </span>
      <button
        type="button"
        className="btn-secondary"
        disabled={page >= totalPages}
        onClick={() => onPageChange(page + 1)}
      >
        {t('pagination.next')}
      </button>
    </nav>
  );
}
