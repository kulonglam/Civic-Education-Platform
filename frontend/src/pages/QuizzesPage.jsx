import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Pagination } from '../components/Pagination';
import { CardSkeleton, EmptyState, PageHeader } from '../components/ui';
import { queryKeys } from '../lib/queryKeys';
import { localizedQuiz } from '../lib/localizedContent';
import { quizService } from '../lib/services';

const PAGE_SIZE = 20;

export function QuizzesPage() {
  const { t, i18n } = useTranslation();
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.quizzes({ page }),
    queryFn: async () => {
      const { data: res } = await quizService.list({ page: String(page) });
      return res;
    },
  });

  const quizzes = data?.results ?? [];
  const totalCount = data?.count ?? 0;

  return (
    <div>
      <PageHeader
        title={t('quizzes.title')}
        action={
          <div className="flex gap-2">
            <Link to="/quizzes/results" className="btn-secondary">
              {t('quizzes.results')}
            </Link>
            <Link to="/quizzes/certificates" className="btn-secondary">
              {t('quizzes.certificates')}
            </Link>
          </div>
        }
      />

      {isLoading ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      ) : quizzes.length === 0 ? (
        <EmptyState>{t('quizzes.noQuizzes')}</EmptyState>
      ) : (
        <>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {quizzes.map((raw) => {
              const quiz = localizedQuiz(raw, i18n.language);
              return (
              <div key={quiz.id} className="card flex flex-col dark:hover:border-slate-600">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-slate-100">{quiz.title}</h3>
                <p className="mt-2 line-clamp-3 flex-1 text-sm text-gray-600 dark:text-slate-400">
                  {quiz.description}
                </p>
                <div className="mt-4 flex items-center justify-between text-xs text-gray-500 dark:text-slate-400">
                  <span>
                    {quiz.questions.length} {t('quizzes.questions')}
                  </span>
                  <span>
                    {t('quizzes.passingScore')}: {quiz.passing_score}%
                  </span>
                </div>
                <Link to={`/quizzes/${quiz.id}`} className="btn-primary mt-4">
                  {t('quizzes.start')}
                </Link>
              </div>
            );})}
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
