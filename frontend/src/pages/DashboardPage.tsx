import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useOrganization } from '../context/OrganizationContext';
import { GamificationSummary } from '../components/GamificationSummary';
import { RecommendationsSection } from '../components/RecommendationsSection';
import { Alert, PageHeader, StatCardSkeleton, StatTile, TableRowSkeleton } from '../components/ui';
import { extractError, isApiStatus } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { analyticsService, organizationService } from '../lib/services';
import type { Id, LearningActivity } from '../types/api';
import { unwrapList } from '../types/api';

function formatDate(value?: string | null) {
  if (!value) return '—';
  return new Date(value).toLocaleDateString();
}

function activityLink(item: LearningActivity) {
  if (item.type === 'article') return `/articles/${item.id}`;
  if (item.type === 'media') return `/media/${item.id}`;
  if (item.type === 'quiz') return `/quizzes/${item.id}`;
  return null;
}

function LearnerDashboard() {
  const { t } = useTranslation();
  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.myLearning,
    queryFn: async () => {
      const { data: res } = await analyticsService.me();
      return res;
    },
  });

  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <StatCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (error) {
    return <Alert>{extractError(error)}</Alert>;
  }

  if (!data) return null;

  const articlePct =
    data.articles_total > 0
      ? Math.round((data.articles_completed / data.articles_total) * 100)
      : 0;
  const mediaPct =
    data.media_total > 0 ? Math.round((data.media_completed / data.media_total) * 100) : 0;

  return (
    <>
      <GamificationSummary className="mb-10" />
      <RecommendationsSection className="mb-10" />

      <section>
        <h2 className="mb-4 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">
          {t('dashboard.myOverview')}
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <StatTile
            label={t('dashboard.articlesCompleted')}
            value={`${data.articles_completed} / ${data.articles_total}`}
          />
          <StatTile label={t('dashboard.articlesInProgress')} value={data.articles_in_progress} />
          <StatTile
            label={t('dashboard.mediaCompleted')}
            value={`${data.media_completed} / ${data.media_total}`}
          />
          <StatTile label={t('dashboard.quizAttempts')} value={data.quizzes_attempted} />
          <StatTile label={t('dashboard.passed')} value={data.quizzes_passed} />
          <StatTile label={t('dashboard.avgScore')} value={`${data.avg_quiz_score}%`} />
          <StatTile label={t('dashboard.certificates')} value={data.certificates} />
          <StatTile label={t('dashboard.articleProgressPct')} value={`${articlePct}%`} />
          <StatTile label={t('dashboard.mediaProgressPct')} value={`${mediaPct}%`} />
        </div>
      </section>

      {data.by_category?.length > 0 && (
        <section className="mt-10">
          <h2 className="mb-4 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">
            {t('dashboard.byCategory')}
          </h2>
          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>{t('dashboard.category')}</th>
                  <th>{t('dashboard.articlesCompleted')}</th>
                  <th>{t('dashboard.mediaCompleted')}</th>
                </tr>
              </thead>
              <tbody>
                {data.by_category.map((row) => (
                  <tr key={row.slug}>
                    <td>{row.category}</td>
                    <td>
                      {row.articles_completed} / {row.articles_total}
                    </td>
                    <td>
                      {row.media_completed} / {row.media_total}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      <section className="mt-10">
        <h2 className="mb-4 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">
          {t('dashboard.recentActivity')}
        </h2>
        {(data.recent_activity ?? []).length === 0 ? (
          <p className="text-sm text-ink-700/60 dark:text-slate-400">{t('dashboard.noRecentActivity')}</p>
        ) : (
          <ul className="space-y-3">
            {data.recent_activity.map((item) => {
              const to = activityLink(item);
              const label =
                item.type === 'quiz' && item.score != null
                  ? `${item.title} · ${item.score}%`
                  : item.title;
              return (
                <li key={`${item.type}-${item.id}-${item.at}`}>
                  {to ? (
                    <Link
                      to={to}
                      className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-ink-100 bg-white/80 px-4 py-3 text-sm transition-colors hover:border-brand-200 dark:border-slate-700 dark:bg-slate-900/50"
                    >
                      <span className="font-medium text-ink-900 dark:text-slate-100">{label}</span>
                      <span className="text-ink-700/55 dark:text-slate-400">
                        {t(`dashboard.activity.${item.type}`)}
                        {item.completed ? ` · ${t('dashboard.completed')}` : ''}
                        {' · '}
                        {formatDate(item.at)}
                      </span>
                    </Link>
                  ) : (
                    <div className="rounded-xl border border-ink-100 px-4 py-3 text-sm dark:border-slate-700">
                      {label}
                    </div>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </>
  );
}

export function DashboardPage() {
  const { t } = useTranslation();
  const { isOrgAdmin } = useOrganization();
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [departmentId, setDepartmentId] = useState('');
  const [departments, setDepartments] = useState<{ id: Id; name: string; slug?: string }[]>([]);
  const [exportError, setExportError] = useState('');

  const filters = {
    from: dateFrom || undefined,
    to: dateTo || undefined,
    department: departmentId || undefined,
  };

  useEffect(() => {
    if (!isOrgAdmin) return;
    organizationService
      .departments()
      .then(({ data }) => setDepartments(unwrapList(data)))
      .catch(() => setDepartments([]));
  }, [isOrgAdmin]);

  const {
    data: dashboard,
    isLoading: dashboardLoading,
    error: dashboardError,
  } = useQuery({
    queryKey: queryKeys.orgDashboard(filters),
    queryFn: async () => {
      const { data } = await analyticsService.dashboard(filters);
      return data;
    },
    enabled: isOrgAdmin,
    retry: (_, error) => !isApiStatus(error, 402),
  });

  const {
    data: progress,
    isLoading: progressLoading,
    error: progressError,
  } = useQuery({
    queryKey: queryKeys.orgProgress(filters),
    queryFn: async () => {
      const { data } = await analyticsService.progress(filters);
      return data.members;
    },
    enabled: isOrgAdmin && !!dashboard,
    retry: (_, error) => !isApiStatus(error, 402),
  });

  const exportCsv = useMutation({
    mutationFn: () => analyticsService.exportCsv(filters),
    onSuccess: (response) => {
      setExportError('');
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'learner-progress.csv';
      link.click();
      URL.revokeObjectURL(url);
    },
    onError: (err) => setExportError(extractError(err)),
  });

  const exportPdf = useMutation({
    mutationFn: () => analyticsService.exportReportPdf(filters),
    onSuccess: (response) => {
      setExportError('');
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'institutional-report.pdf';
      link.click();
      URL.revokeObjectURL(url);
    },
    onError: (err) => setExportError(extractError(err)),
  });

  if (!isOrgAdmin) {
    return (
      <div className="page-shell">
        <PageHeader
          eyebrow={t('dashboard.myEyebrow')}
          title={t('dashboard.myTitle')}
          subtitle={t('dashboard.mySubtitle')}
        />
        <LearnerDashboard />
      </div>
    );
  }

  if (dashboardLoading) {
    return (
      <div className="page-shell">
        <PageHeader eyebrow={t('dashboard.eyebrow')} title={t('dashboard.title')} subtitle={t('dashboard.subtitle')} />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => <StatCardSkeleton key={i} />)}
        </div>
        <div className="data-table-wrap">
          <table className="data-table">
            <tbody>
              {Array.from({ length: 5 }).map((_, i) => <TableRowSkeleton key={i} cols={9} />)}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  const needsUpgrade =
    isApiStatus(dashboardError, 402) || isApiStatus(progressError, 402);

  if (needsUpgrade) {
    return (
      <div className="page-shell">
        <PageHeader eyebrow={t('dashboard.eyebrow')} title={t('dashboard.title')} subtitle={t('dashboard.subtitle')} />
        <div className="surface px-6 py-10 text-center sm:px-10">
          <Alert kind="warning">{t('dashboard.upgradeRequired')}</Alert>
          <Link to="/billing" className="btn-primary mt-6 inline-block">
            {t('saas.upgradePlan')}
          </Link>
        </div>
      </div>
    );
  }

  if (dashboardError) {
    return (
      <div className="page-shell">
        <PageHeader eyebrow={t('dashboard.eyebrow')} title={t('dashboard.title')} />
        <Alert>{extractError(dashboardError)}</Alert>
      </div>
    );
  }

  if (!dashboard) return null;

  return (
    <div className="page-shell">
      <PageHeader eyebrow={t('dashboard.eyebrow')} title={t('dashboard.title')} subtitle={t('dashboard.subtitle')} />

      <section className="filter-bar">
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="label" htmlFor="date-from">
              {t('dashboard.dateFrom')}
            </label>
            <input
              id="date-from"
              type="date"
              className="input"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
            />
          </div>
          <div>
            <label className="label" htmlFor="date-to">
              {t('dashboard.dateTo')}
            </label>
            <input
              id="date-to"
              type="date"
              className="input"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
            />
          </div>
          <div>
            <label className="label" htmlFor="department">
              {t('saas.departments')}
            </label>
            <select
              id="department"
              className="input"
              value={departmentId}
              onChange={(e) => setDepartmentId(e.target.value)}
            >
              <option value="">{t('dashboard.allDepartments')}</option>
              {departments.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </div>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => {
              setDateFrom('');
              setDateTo('');
              setDepartmentId('');
            }}
          >
            {t('dashboard.clearDates')}
          </button>
          <button
            type="button"
            className="btn-primary"
            disabled={exportCsv.isPending}
            onClick={() => exportCsv.mutate()}
          >
            {exportCsv.isPending ? t('common.loading') : t('dashboard.exportCsv')}
          </button>
          <button
            type="button"
            className="btn-secondary"
            disabled={exportPdf.isPending}
            onClick={() => exportPdf.mutate()}
          >
            {exportPdf.isPending ? t('common.loading') : t('dashboard.exportReportPdf')}
          </button>
        </div>
        {exportError && (
          <div className="mt-4">
            <Alert>{exportError}</Alert>
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-4 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">{t('dashboard.overview')}</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <StatTile label={t('dashboard.totalMembers')} value={dashboard.total_members} />
          <StatTile label={t('dashboard.activeMembers')} value={dashboard.active_members_30d} />
          <StatTile label={t('dashboard.quizAttempts')} value={dashboard.quiz_attempts} />
          <StatTile label={t('dashboard.passRate')} value={`${dashboard.quiz_pass_rate}%`} />
          <StatTile label={t('dashboard.certificates')} value={dashboard.certificates_issued} />
          <StatTile label={t('dashboard.publishedArticles')} value={dashboard.published_articles} />
        </div>
      </section>

      <section>
        <h2 className="mb-4 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">{t('dashboard.memberProgress')}</h2>
        <div className="data-table-wrap">
        {progressLoading ? (
          <table className="data-table">
            <tbody>
              {Array.from({ length: 4 }).map((_, i) => <TableRowSkeleton key={i} cols={9} />)}
            </tbody>
          </table>
        ) : (
          <div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>{t('dashboard.member')}</th>
                  <th>{t('dashboard.role')}</th>
                  <th>{t('saas.departments')}</th>
                  <th>{t('dashboard.attempted')}</th>
                  <th>{t('dashboard.passed')}</th>
                  <th>{t('dashboard.avgScore')}</th>
                  <th>{t('dashboard.articlesCompleted')}</th>
                  <th>{t('dashboard.mediaCompleted')}</th>
                  <th>{t('dashboard.certificates')}</th>
                  <th>{t('dashboard.lastActivity')}</th>
                </tr>
              </thead>
              <tbody>
                {(progress ?? []).map((row) => (
                  <tr key={row.user_id}>
                    <td>
                      <p className="font-semibold text-ink-900 dark:text-slate-100">
                        {row.first_name} {row.last_name}
                      </p>
                      <p className="text-xs text-ink-700/55 dark:text-slate-400">{row.email}</p>
                    </td>
                    <td className="capitalize">{row.role}</td>
                    <td>{row.department || '—'}</td>
                    <td>{row.quizzes_attempted}</td>
                    <td>{row.quizzes_passed}</td>
                    <td>{row.avg_score}%</td>
                    <td>{row.articles_completed ?? 0}</td>
                    <td>{row.media_completed ?? 0}</td>
                    <td>{row.certificates}</td>
                    <td className="text-ink-700/65 dark:text-slate-400">{formatDate(row.last_activity)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {(progress ?? []).length === 0 && (
              <p className="px-4 py-8 text-center text-sm text-ink-700/60 dark:text-slate-400">{t('dashboard.noProgress')}</p>
            )}
          </div>
        )}
        </div>
      </section>
    </div>
  );
}
