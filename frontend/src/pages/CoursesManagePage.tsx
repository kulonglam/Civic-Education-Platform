// @ts-nocheck
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Alert, ConfirmDialog, EmptyState, Spinner } from '../components/ui';
import { CmsManageHeader, StatusBadge } from '../components/CmsWorkspace';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { courseService } from '../lib/services';

export function CoursesManagePage() {
  const { t } = useTranslation();
  const { hasRole } = useAuth();
  const { isOrgAdmin } = useOrganization();
  const canDelete = hasRole('admin') || isOrgAdmin;
  const [pendingDelete, setPendingDelete] = useState(null);
  const [deleteError, setDeleteError] = useState('');
  const [deleting, setDeleting] = useState(false);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: queryKeys.coursesManage,
    queryFn: async () => {
      const { data: res } = await courseService.list({ page_size: '100' });
      return res.results ?? res;
    },
  });

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setDeleting(true);
    setDeleteError('');
    try {
      await courseService.remove(pendingDelete.id);
      setPendingDelete(null);
      await refetch();
    } catch (err) {
      setDeleteError(extractError(err));
    } finally {
      setDeleting(false);
    }
  };

  if (isLoading) return <Spinner />;
  const items = data ?? [];

  return (
    <div>
      <CmsManageHeader
        title={t('courses.manageTitle')}
        subtitle={t('courses.manageSubtitle')}
        primaryTo="/courses/new"
        primaryLabel={t('courses.create')}
      />
      {error && <Alert>{extractError(error)}</Alert>}
      {deleteError && <Alert>{deleteError}</Alert>}
      {items.length === 0 ? (
        <EmptyState title={t('courses.emptyManage')} />
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-ink-100 bg-white dark:border-slate-800 dark:bg-slate-900">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-ink-50 text-ink-700 dark:bg-slate-800 dark:text-slate-300">
              <tr>
                <th className="px-4 py-3 font-medium">{t('courses.fields.title')}</th>
                <th className="px-4 py-3 font-medium">{t('courses.fields.lessons')}</th>
                <th className="px-4 py-3 font-medium">{t('courses.fields.status')}</th>
                <th className="px-4 py-3 font-medium">{t('common.edit')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-100 dark:divide-slate-700">
              {items.map((item) => (
                <tr key={item.id}>
                  <td className="px-4 py-3 font-medium">
                    <Link to={`/courses/${item.id}`} className="hover:underline">{item.title}</Link>
                  </td>
                  <td className="px-4 py-3">{item.lesson_count}</td>
                  <td className="px-4 py-3"><StatusBadge status={item.status} label={t(`courses.status.${item.status}`, { defaultValue: item.status })} /></td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      <Link to={`/courses/${item.id}/edit`} className="btn-secondary text-xs">{t('common.edit')}</Link>
                      {canDelete && (
                        <button
                          type="button"
                          className="btn-danger text-xs"
                          onClick={() => setPendingDelete({ id: item.id, title: item.title })}
                        >
                          {t('common.delete')}
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title={t('common.confirmDelete')}
        message={pendingDelete ? t('courses.deleteConfirm', { title: pendingDelete.title }) : ''}
        confirmLabel={t('common.delete')}
        onConfirm={confirmDelete}
        onCancel={() => !deleting && setPendingDelete(null)}
        busy={deleting}
      />
    </div>
  );
}
