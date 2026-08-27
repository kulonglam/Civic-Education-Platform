// @ts-nocheck
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import { Alert, ConfirmDialog, EmptyState, Spinner } from '../components/ui';
import { CmsManageHeader, StatusBadge } from '../components/CmsWorkspace';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { mediaService } from '../lib/services';
import { formatDate } from '../lib/format';

export function MediaManagePage() {
  const { t } = useTranslation();
  const { hasRole } = useAuth();
  const { isOrgAdmin } = useOrganization();
  const canDelete = hasRole('admin') || isOrgAdmin;
  const [pendingDelete, setPendingDelete] = useState(null);
  const [deleteError, setDeleteError] = useState('');
  const [deleting, setDeleting] = useState(false);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: queryKeys.mediaManage,
    queryFn: async () => {
      const { data: res } = await mediaService.list({ page_size: '100' });
      return res.results ?? res;
    },
  });

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setDeleting(true);
    setDeleteError('');
    try {
      await mediaService.remove(pendingDelete.id);
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
        title={t('media.manageTitle')}
        subtitle={t('media.manageSubtitle')}
        primaryTo="/media/new"
        primaryLabel={t('media.create')}
      />
      {error && <Alert>{extractError(error)}</Alert>}
      {deleteError && (
        <div className="mb-4">
          <Alert>{deleteError}</Alert>
        </div>
      )}
      {items.length === 0 ? (
        <EmptyState>{t('media.empty')}</EmptyState>
      ) : (
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>{t('media.fieldTitle')}</th>
                <th>{t('media.fieldType')}</th>
                <th>{t('media.fieldStatus')}</th>
                <th>{t('media.fieldPublished')}</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td>
                    <Link
                      to={`/media/${item.id}`}
                      className="font-medium text-brand-700 hover:underline dark:text-brand-400"
                    >
                      {item.title}
                    </Link>
                  </td>
                  <td>
                    {item.media_type === 'audio'
                      ? t('media.typeAudio')
                      : t('media.typeVideo')}
                  </td>
                  <td>
                    <StatusBadge status={item.status} label={item.status} />
                  </td>
                  <td>{item.published_at ? formatDate(item.published_at) : '—'}</td>
                  <td className="space-x-2 text-right">
                    <Link
                      to={`/media/${item.id}/edit`}
                      className="text-sm font-medium text-brand-700 hover:underline dark:text-brand-400"
                    >
                      {t('common.edit')}
                    </Link>
                    {canDelete && (
                      <button
                        type="button"
                        className="text-sm font-medium text-red-600 hover:underline"
                        onClick={() => setPendingDelete(item)}
                      >
                        {t('common.delete')}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <ConfirmDialog
        open={!!pendingDelete}
        title={t('common.confirmDelete')}
        message={pendingDelete ? pendingDelete.title : ''}
        confirmLabel={t('common.delete')}
        busy={deleting}
        onConfirm={confirmDelete}
        onCancel={() => {
          setPendingDelete(null);
          setDeleteError('');
        }}
      />
    </div>
  );
}
