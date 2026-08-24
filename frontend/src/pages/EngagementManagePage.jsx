import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Alert, ConfirmDialog, EmptyState, PageHeader, Spinner } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { engagementService } from '../lib/services';

const TABS = ['polls', 'petitions', 'campaigns'];

export function EngagementManagePage() {
  const { t } = useTranslation();
  const { hasRole } = useAuth();
  const { isOrgAdmin } = useOrganization();
  const canDelete = hasRole('admin') || isOrgAdmin;
  const [tab, setTab] = useState('polls');
  const [pendingDelete, setPendingDelete] = useState(null);
  const [deleteError, setDeleteError] = useState('');
  const [deleting, setDeleting] = useState(false);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: queryKeys.engagementManage(tab),
    queryFn: async () => {
      const params = { manage: '1' };
      if (tab === 'polls') {
        const { data: res } = await engagementService.polls(params);
        return res.results ?? res;
      }
      if (tab === 'petitions') {
        const { data: res } = await engagementService.petitions(params);
        return res.results ?? res;
      }
      const { data: res } = await engagementService.campaigns(params);
      return res.results ?? res;
    },
  });

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setDeleting(true);
    setDeleteError('');
    try {
      if (pendingDelete.kind === 'polls') await engagementService.removePoll(pendingDelete.id);
      else if (pendingDelete.kind === 'petitions') await engagementService.removePetition(pendingDelete.id);
      else await engagementService.removeCampaign(pendingDelete.id);
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
  const titleOf = (item) => item.question || item.title;

  return (
    <div>
      <PageHeader
        eyebrow={t('nav.manage')}
        title={t('engage.manageTitle')}
        subtitle={t('engage.manageSubtitle')}
      />
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2">
          {TABS.map((key) => (
            <button
              key={key}
              type="button"
              className={tab === key ? 'btn-primary text-sm' : 'btn-secondary text-sm'}
              onClick={() => setTab(key)}
            >
              {t(`engage.${key}`)}
            </button>
          ))}
        </div>
        <Link to={`/engage/${tab}/new`} className="btn-primary text-sm">
          {t(`engage.create_${tab}`)}
        </Link>
      </div>
      {error && <Alert>{extractError(error)}</Alert>}
      {deleteError && <Alert>{deleteError}</Alert>}
      {items.length === 0 ? (
        <EmptyState title={t('engage.emptyManage')} />
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-ink-100 bg-white dark:border-slate-800 dark:bg-slate-900">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-ink-50 text-ink-700 dark:bg-slate-800 dark:text-slate-300">
              <tr>
                <th className="px-4 py-3 font-medium">{t('engage.fields.title')}</th>
                <th className="px-4 py-3 font-medium">{t('engage.fields.status')}</th>
                <th className="px-4 py-3 font-medium">{t('common.edit')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-slate-700">
              {items.map((item) => (
                <tr key={item.id} className="dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-medium text-gray-900 dark:text-slate-100">
                    {titleOf(item)}
                  </td>
                  <td className="px-4 py-3 dark:text-slate-300">
                    {t(`engage.status.${item.status}`, { defaultValue: item.status })}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      <Link to={`/engage/${tab}/${item.id}/edit`} className="btn-secondary text-xs">
                        {t('common.edit')}
                      </Link>
                      {canDelete && (
                        <button
                          type="button"
                          className="btn-danger text-xs"
                          onClick={() => {
                            setDeleteError('');
                            setPendingDelete({ id: item.id, title: titleOf(item), kind: tab });
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
        message={pendingDelete ? t('engage.deleteConfirm', { title: pendingDelete.title }) : ''}
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
