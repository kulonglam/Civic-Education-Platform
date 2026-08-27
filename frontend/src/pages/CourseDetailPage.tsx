// @ts-nocheck
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { Alert, EmptyState, PageHeader, Spinner } from '../components/ui';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { courseService } from '../lib/services';

export function CourseDetailPage() {
  const { t } = useTranslation();
  const { id } = useParams();
  const { data: course, isLoading, error } = useQuery({
    queryKey: queryKeys.course(id),
    queryFn: async () => {
      const { data } = await courseService.get(id);
      return data;
    },
  });

  if (isLoading) return <Spinner />;
  if (error) return <Alert>{extractError(error)}</Alert>;
  if (!course) return <EmptyState title={t('courses.notFound')} />;

  const lessons = course.lessons ?? [];

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader title={course.title} subtitle={course.description} />
      <p className="mb-6 text-sm text-ink-700/70 dark:text-slate-400">
        {t('courses.progress', {
          done: course.completed_count || 0,
          total: course.lesson_count || 0,
          pct: course.lesson_count
            ? Math.round(((course.completed_count || 0) / course.lesson_count) * 100)
            : 0,
        })}
      </p>
      {lessons.length === 0 ? (
        <EmptyState title={t('courses.noLessons')} />
      ) : (
        <ol className="space-y-3">
          {lessons.map((lesson, index) => (
            <li key={lesson.id}>
              <Link
                to={`/articles/${lesson.article_id}`}
                className="flex items-start gap-3 rounded-2xl border border-ink-100 bg-white p-4 hover:border-brand-200 dark:border-slate-800 dark:bg-slate-900"
              >
                <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-50 text-sm font-semibold text-brand-800 dark:bg-brand-900/40 dark:text-brand-200">
                  {index + 1}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-ink-900 dark:text-slate-100">{lesson.title}</p>
                  <p className="text-xs text-ink-700/60 dark:text-slate-400">
                    {lesson.completed ? t('courses.completed') : t('courses.notStarted')}
                  </p>
                </div>
              </Link>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
