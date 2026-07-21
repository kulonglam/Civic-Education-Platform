import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useOrganization } from '../context/OrganizationContext';
import { Alert, PageHeader, StatCardSkeleton, StatTile, TableRowSkeleton } from '../components/ui';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { analyticsService, organizationService } from '../lib/services';

function formatDate(value) {
  if (!value) return '—';
  return new Date(value).toLocaleDateString();
}

export function DashboardPage() {
  const { t } = useTranslation();
  const { isOrgAdmin } = useOrganization();
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [departmentId, setDepartmentId] = useState('');
  const [departments, setDepartments] = useState([]);
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
      .then(({ data }) => setDepartments(Array.isArray(data) ? data : data.results ?? []))
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
    retry: (_, error) => error?.response?.status !== 402,
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
    retry: (_, error) => error?.response?.status !== 402,
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
        <PageHeader eyebrow={t('dashboard.eyebrow')} title={t('dashboard.title')} />
        <Alert>{t('dashboard.adminOnly')}</Alert>
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
              {Array.from({ length: 5 }).map((_, i) => <TableRowSkeleton key={i} cols={7} />)}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  const needsUpgrade =
    dashboardError?.response?.status === 402 || progressError?.response?.status === 402;

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
              {Array.from({ length: 4 }).map((_, i) => <TableRowSkeleton key={i} cols={7} />)}
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
