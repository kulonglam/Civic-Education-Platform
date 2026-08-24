import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { EventKindBadge } from '../components/EventKindBadge';
import { Alert, ConfirmDialog, EmptyState, PageHeader, Spinner } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import { extractError } from '../lib/api';
import { formatDateTime } from '../lib/format';
import { queryKeys } from '../lib/queryKeys';
import { eventsService } from '../lib/services';

export function EventsManagePage() {
  const { t } = useTranslation();
  const { hasRole } = useAuth();
  const { isOrgAdmin } = useOrganization();
  const canDelete = hasRole('admin') || isOrgAdmin;
  const [pendingDelete, setPendingDelete] = useState(null);
  const [deleteError, setDeleteError] = useState('');
  const [deleting, setDeleting] = useState(false);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: queryKeys.eventsManage,
    queryFn: async () => {
      const { data: res } = await eventsService.list({ page_size: '100' });
      return res.results ?? res;
    },
  });

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setDeleting(true);
    setDeleteError('');
    try {
      await eventsService.remove(pendingDelete.id);
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
      <PageHeader
        eyebrow={t('nav.manage')}
        title={t('events.manageTitle')}
        subtitle={t('events.manageSubtitle')}
      />
      <div className="mb-4 flex justify-end">
        <Link to="/events/new" className="btn-primary text-sm">
          {t('events.create')}
        </Link>
      </div>
      {error && <Alert>{extractError(error)}</Alert>}
      {deleteError && <Alert>{deleteError}</Alert>}
      {items.length === 0 ? (
        <EmptyState title={t('events.emptyManage')} />
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-ink-100 bg-white dark:border-slate-800 dark:bg-slate-900">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-ink-50 text-ink-700 dark:bg-slate-800 dark:text-slate-300">
              <tr>
                <th className="px-4 py-3 font-medium">{t('events.fields.title')}</th>
                <th className="px-4 py-3 font-medium">{t('events.fields.kind')}</th>
                <th className="px-4 py-3 font-medium">{t('events.fields.startsAt')}</th>
                <th className="px-4 py-3 font-medium">{t('events.fields.status')}</th>
                <th className="px-4 py-3 font-medium">{t('common.edit')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-slate-700">
              {items.map((item) => (
                <tr key={item.id} className="dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-medium text-gray-900 dark:text-slate-100">
                    <Link to={`/events/${item.id}`} className="hover:underline">
                      {item.title}
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <EventKindBadge kind={item.kind} />
                  </td>
                  <td className="px-4 py-3 dark:text-slate-300">{formatDateTime(item.starts_at)}</td>
                  <td className="px-4 py-3 dark:text-slate-300">{t(`events.status.${item.status}`)}</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      <Link to={`/events/${item.id}/edit`} className="btn-secondary text-xs">
                        {t('common.edit')}
                      </Link>
                      {canDelete && (
                        <button
                          type="button"
                          className="btn-danger text-xs"
                          onClick={() => {
                            setDeleteError('');
                            setPendingDelete({ id: item.id, title: item.title });
                          }}
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
        message={pendingDelete ? t('events.deleteConfirm', { title: pendingDelete.title }) : ''}
        confirmLabel={t('common.delete')}
        onConfirm={confirmDelete}
        onCancel={() => {
          if (deleting) return;
          setPendingDelete(null);
          setDeleteError('');
        }}
        busy={deleting}
      />
    </div>
  );
}
