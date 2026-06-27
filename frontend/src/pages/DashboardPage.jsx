import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useOrganization } from '../context/OrganizationContext';
import { Alert, PageHeader, Spinner, StatCardSkeleton, TableRowSkeleton } from '../components/ui';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { analyticsService } from '../lib/services';

function StatCard({ label, value }) {
  return (
    <div className="card">
      <p className="text-sm text-gray-500 dark:text-slate-400">{label}</p>
      <p className="mt-1 text-3xl font-bold text-gray-900 dark:text-slate-100">{value}</p>
    </div>
  );
}

function formatDate(value) {
  if (!value) return '—';
  return new Date(value).toLocaleDateString();
}

export function DashboardPage() {
  const { t } = useTranslation();
  const { isOrgAdmin } = useOrganization();
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [exportError, setExportError] = useState('');

  const filters = { from: dateFrom || undefined, to: dateTo || undefined };

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

  if (!isOrgAdmin) {
    return (
      <div>
        <PageHeader title={t('dashboard.title')} />
        <Alert>{t('dashboard.adminOnly')}</Alert>
      </div>
    );
  }

  if (dashboardLoading) {
    return (
      <div className="space-y-10">
        <PageHeader title={t('dashboard.title')} subtitle={t('dashboard.subtitle')} />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => <StatCardSkeleton key={i} />)}
        </div>
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-slate-700 dark:bg-slate-800">
          <table className="w-full text-sm">
            <tbody className="divide-y divide-gray-100 dark:divide-slate-700">
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
      <div>
        <PageHeader title={t('dashboard.title')} subtitle={t('dashboard.subtitle')} />
        <div className="card">
          <Alert kind="warning">{t('dashboard.upgradeRequired')}</Alert>
          <Link to="/billing" className="btn-primary mt-4 inline-block">
            {t('saas.upgradePlan')}
          </Link>
        </div>
      </div>
    );
  }

  if (dashboardError) {
    return (
      <div>
        <PageHeader title={t('dashboard.title')} />
        <Alert>{extractError(dashboardError)}</Alert>
      </div>
    );
  }

  return (
    <div className="space-y-10">
      <PageHeader title={t('dashboard.title')} subtitle={t('dashboard.subtitle')} />

      <section className="card">
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-slate-300" htmlFor="date-from">
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
            <label className="mb-1 block text-sm font-medium text-gray-700 dark:text-slate-300" htmlFor="date-to">
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
          <button
            type="button"
            className="btn-secondary"
            onClick={() => {
              setDateFrom('');
              setDateTo('');
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
        </div>
        {exportError && (
          <div className="mt-4">
            <Alert>{exportError}</Alert>
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('dashboard.overview')}</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <StatCard label={t('dashboard.totalMembers')} value={dashboard.total_members} />
          <StatCard label={t('dashboard.activeMembers')} value={dashboard.active_members_30d} />
          <StatCard label={t('dashboard.quizAttempts')} value={dashboard.quiz_attempts} />
          <StatCard label={t('dashboard.passRate')} value={`${dashboard.quiz_pass_rate}%`} />
          <StatCard label={t('dashboard.certificates')} value={dashboard.certificates_issued} />
          <StatCard label={t('dashboard.publishedArticles')} value={dashboard.published_articles} />
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-slate-100">{t('dashboard.memberProgress')}</h2>
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-slate-700 dark:bg-slate-800">
        {progressLoading ? (
          <table className="w-full text-sm">
            <tbody className="divide-y divide-gray-100 dark:divide-slate-700">
              {Array.from({ length: 4 }).map((_, i) => <TableRowSkeleton key={i} cols={7} />)}
            </tbody>
          </table>
        ) : (
          <div>
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-left text-gray-500 dark:bg-slate-700/50 dark:text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-medium">{t('dashboard.member')}</th>
                  <th className="px-4 py-3 font-medium">{t('dashboard.role')}</th>
                  <th className="px-4 py-3 font-medium">{t('dashboard.attempted')}</th>
                  <th className="px-4 py-3 font-medium">{t('dashboard.passed')}</th>
                  <th className="px-4 py-3 font-medium">{t('dashboard.avgScore')}</th>
                  <th className="px-4 py-3 font-medium">{t('dashboard.certificates')}</th>
                  <th className="px-4 py-3 font-medium">{t('dashboard.lastActivity')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-slate-700">
                {(progress ?? []).map((row) => (
                  <tr key={row.user_id} className="dark:hover:bg-slate-700/30">
                    <td className="px-4 py-3">
                      <p className="font-medium text-gray-900 dark:text-slate-100">
                        {row.first_name} {row.last_name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-slate-400">{row.email}</p>
                    </td>
                    <td className="px-4 py-3 capitalize dark:text-slate-300">{row.role}</td>
                    <td className="px-4 py-3 dark:text-slate-300">{row.quizzes_attempted}</td>
                    <td className="px-4 py-3 dark:text-slate-300">{row.quizzes_passed}</td>
                    <td className="px-4 py-3 dark:text-slate-300">{row.avg_score}%</td>
                    <td className="px-4 py-3 dark:text-slate-300">{row.certificates}</td>
                    <td className="px-4 py-3 dark:text-slate-400">{formatDate(row.last_activity)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {(progress ?? []).length === 0 && (
              <p className="px-4 py-8 text-center text-gray-500 dark:text-slate-400">{t('dashboard.noProgress')}</p>
            )}
          </div>
        )}
        </div>
      </section>
    </div>
  );
}
