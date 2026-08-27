// @ts-nocheck
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Pagination } from '../components/Pagination';
import { CardSkeleton, EmptyState, PageHeader } from '../components/ui';
import { queryKeys } from '../lib/queryKeys';
import { localizedQuiz } from '../lib/localizedContent';
import { quizService } from '../lib/services';
import { useAuth } from '../context/AuthContext';
import { GuestSaveCta } from '../components/GuestSaveCta';

const PAGE_SIZE = 20;

export function QuizzesPage() {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
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
    <div className="page-shell">
      <PageHeader
        eyebrow={t('nav.learn')}
        title={t('quizzes.title')}
        subtitle={t('quizzes.subtitle')}
        action={
          user ? (
            <div className="flex gap-2">
              <Link to="/quizzes/results" className="btn-secondary">
                {t('quizzes.results')}
              </Link>
              <Link to="/quizzes/certificates" className="btn-secondary">
                {t('quizzes.certificates')}
              </Link>
            </div>
          ) : null
        }
      />

      {!user && <GuestSaveCta className="mb-6" />}

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      ) : quizzes.length === 0 ? (
        <EmptyState title={t('quizzes.noQuizzes')}>{t('common.noResults')}</EmptyState>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {quizzes.map((raw) => {
              const quiz = localizedQuiz(raw, i18n.language);
              return (
                <div key={quiz.id} className="content-tile">
                  <h3 className="font-display text-lg font-semibold text-ink-900 dark:text-slate-100">
                    {quiz.title}
                  </h3>
                  <p className="mt-2 line-clamp-3 flex-1 text-sm leading-relaxed text-ink-700/75 dark:text-slate-400">
                    {quiz.description}
                  </p>
                  <div className="content-meta">
                    <span>
                      {quiz.kind === 'practice' ? t('quizzes.kindPractice') : t('quizzes.kindAssessment')}
                    </span>
                    <span aria-hidden="true">·</span>
                    <span>
                      {quiz.question_count ?? quiz.questions?.length ?? 0} {t('quizzes.questions')}
                    </span>
                    <span aria-hidden="true">·</span>
                    <span>
                      {t('quizzes.passingScore')}: {quiz.passing_score}%
                    </span>
                  </div>
                  {user ? (
                    <Link to={`/quizzes/${quiz.id}`} className="btn-primary mt-5 w-full">
                      {t('quizzes.start')}
                    </Link>
                  ) : (
                    <Link
                      to="/register"
                      state={{ from: `/quizzes/${quiz.id}` }}
                      className="btn-primary mt-5 w-full"
                    >
                      {t('guest.createAccountToStart')}
                    </Link>
                  )}
                </div>
              );
            })}
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
