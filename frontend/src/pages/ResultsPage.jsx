import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Pagination } from '../components/Pagination';
import { TableRowSkeleton } from '../components/ui';
import { EmptyState, PageHeader } from '../components/ui';
import { queryKeys } from '../lib/queryKeys';
import { formatDate } from '../lib/format';
import { quizService } from '../lib/services';

const PAGE_SIZE = 20;

export function ResultsPage() {
  const { t } = useTranslation();
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.quizResults({ page }),
    queryFn: async () => {
      const { data: res } = await quizService.results({ page: String(page) });
      return res;
    },
  });

  const attempts = data?.results ?? [];
  const totalCount = data?.count ?? 0;

  return (
    <div>
      <PageHeader
        title={t('quizzes.results')}
        action={
          <Link to="/quizzes" className="btn-secondary">
            {t('common.back')}
          </Link>
        }
      />

      {isLoading ? (
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-slate-700 dark:bg-slate-800">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-gray-500 dark:bg-slate-700/50 dark:text-slate-400">
              <tr>
                <th className="px-4 py-3 font-medium">{t('quizzes.title')}</th>
                <th className="px-4 py-3 font-medium">{t('quizzes.yourScore')}</th>
                <th className="px-4 py-3 font-medium">{t('common.approved')}</th>
                <th className="px-4 py-3 font-medium">{t('quizzes.issued')}</th>
              </tr>
            </thead>
            <tbody>
              <TableRowSkeleton cols={4} rows={5} />
            </tbody>
          </table>
        </div>
      ) : attempts.length === 0 ? (
        <EmptyState>{t('common.noResults')}</EmptyState>
      ) : (
        <>
          <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-slate-700 dark:bg-slate-800">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-left text-gray-500 dark:bg-slate-700/50 dark:text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-medium">{t('quizzes.title')}</th>
                  <th className="px-4 py-3 font-medium">{t('quizzes.yourScore')}</th>
                  <th className="px-4 py-3 font-medium">{t('common.approved')}</th>
                  <th className="px-4 py-3 font-medium">{t('quizzes.issued')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-slate-700">
                {attempts.map((a) => (
                  <tr key={a.id} className="dark:hover:bg-slate-700/30">
                    <td className="px-4 py-3 font-medium text-gray-900 dark:text-slate-100">{a.quiz_title}</td>
                    <td className="px-4 py-3 dark:text-slate-300">{a.score}%</td>
                    <td className="px-4 py-3">
                      <span
                        className={`badge ${a.passed ? 'bg-green-100 text-green-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'}`}
                      >
                        {a.passed ? t('quizzes.passed') : t('quizzes.failed')}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-500 dark:text-slate-400">{formatDate(a.attempted_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination
            page={page}
            totalCount={totalCount}
            pageSize={PAGE_SIZE}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  );
}
