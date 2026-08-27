// @ts-nocheck
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Alert, EmptyState, PageHeader, Spinner } from '../components/ui';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { courseService } from '../lib/services';

export function CoursesPage() {
  const { t } = useTranslation();
  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.courses(),
    queryFn: async () => {
      const { data: res } = await courseService.list({ page_size: '50' });
      return res.results ?? res;
    },
  });

  if (isLoading) return <Spinner />;
  const courses = data ?? [];

  return (
    <div>
      <PageHeader title={t('courses.title')} subtitle={t('courses.subtitle')} />
      {error && <Alert>{extractError(error)}</Alert>}
      {courses.length === 0 ? (
        <EmptyState title={t('courses.empty')} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {courses.map((course) => {
            const total = course.lesson_count || 0;
            const done = course.completed_count || 0;
            const pct = total ? Math.round((done / total) * 100) : 0;
            return (
              <Link key={course.id} to={`/courses/${course.id}`} className="content-tile group">
                <h3 className="font-display text-lg font-semibold text-ink-900 group-hover:text-brand-700 dark:text-slate-100">
                  {course.title}
                </h3>
                {course.description && (
                  <p className="mt-2 line-clamp-3 text-sm text-ink-700/75 dark:text-slate-400">
                    {course.description}
                  </p>
                )}
                <p className="mt-4 text-xs text-ink-700/60 dark:text-slate-400">
                  {t('courses.progress', { done, total, pct })}
                </p>
                <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-ink-100 dark:bg-slate-700">
                  <div className="h-full bg-brand-600" style={{ width: `${pct}%` }} />
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
