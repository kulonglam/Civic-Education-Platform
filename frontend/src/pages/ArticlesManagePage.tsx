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
import { articleService } from '../lib/services';
import { formatDate } from '../lib/format';
import type { Article, Id } from '../types/api';

export function ArticlesManagePage() {
  const { t } = useTranslation();
  const { hasRole } = useAuth();
  const { membership, isOrgAdmin } = useOrganization();
  const canDelete = hasRole('admin') || isOrgAdmin;
  const canApprove =
    hasRole('admin') || membership?.role === 'owner' || membership?.role === 'admin';
  const [pendingDelete, setPendingDelete] = useState<Article | null>(null);
  const [deleteError, setDeleteError] = useState('');
  const [reviewError, setReviewError] = useState('');
  const [deleting, setDeleting] = useState(false);
  const [reviewBusyId, setReviewBusyId] = useState<Id | null>(null);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: queryKeys.articlesManage,
    queryFn: async () => {
      const { data: res } = await articleService.list({ page_size: '100' });
      return res.results ?? res;
    },
  });

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setDeleting(true);
    setDeleteError('');
    try {
      await articleService.remove(pendingDelete.id);
      setPendingDelete(null);
      await refetch();
    } catch (err) {
      setDeleteError(extractError(err));
    } finally {
      setDeleting(false);
    }
  };

  const approveArticle = async (id: Id) => {
    setReviewBusyId(id);
    setReviewError('');
    try {
      await articleService.approve(id);
      await refetch();
    } catch (err) {
      setReviewError(extractError(err));
    } finally {
      setReviewBusyId(null);
    }
  };

  const rejectArticle = async (id: Id) => {
    setReviewBusyId(id);
    setReviewError('');
    try {
      await articleService.reject(id);
      await refetch();
    } catch (err) {
      setReviewError(extractError(err));
    } finally {
      setReviewBusyId(null);
    }
  };

  if (isLoading) return <Spinner />;

  const articles = data ?? [];

  return (
    <div>
      <CmsManageHeader
        title={t('articles.manageTitle')}
        subtitle={t('articles.manageSubtitle')}
        primaryTo="/articles/new"
        primaryLabel={t('articles.create')}
        secondary={
          <>
            <Link to="/categories/manage" className="btn-secondary">
              {t('categories.manageTitle')}
            </Link>
            <Link to="/articles" className="btn-secondary">
              {t('articles.viewPublic')}
            </Link>
          </>
        }
      />

      {error && (
        <div className="mb-4">
          <Alert>{extractError(error)}</Alert>
        </div>
      )}
      {deleteError && (
        <div className="mb-4">
          <Alert>{deleteError}</Alert>
        </div>
      )}
      {reviewError && (
        <div className="mb-4">
          <Alert>{reviewError}</Alert>
        </div>
      )}

      {articles.length === 0 ? (
        <EmptyState>{t('articles.noArticlesManage')}</EmptyState>
      ) : (
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                  <th>{t('articles.fieldTitle')}</th>
                <th>{t('articles.category')}</th>
                <th>{t('articles.fieldStatus')}</th>
                <th>{t('articles.updated')}</th>
                <th>{t('common.edit')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-100 dark:divide-slate-700">
              {articles.map((article) => (
                <tr key={article.id} className="dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-medium text-ink-900 dark:text-slate-100">{article.title}</td>
                  <td className="px-4 py-3 dark:text-slate-300">{article.category?.name ?? '—'}</td>
                  <td className="px-4 py-3">
                    <StatusBadge
                      status={article.status}
                      label={
                        article.status === 'pending_review'
                          ? t('articles.statusPendingReview')
                          : article.status === 'published'
                            ? t('articles.statusPublished')
                            : article.status === 'archived'
                              ? t('articles.statusArchived')
                              : t('articles.statusDraft')
                      }
                    />
                  </td>
                  <td className="px-4 py-3 dark:text-slate-400">{formatDate(article.updated_at)}</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      <Link to={`/articles/${article.id}/edit`} className="btn-secondary text-xs">
                        {t('common.edit')}
                      </Link>
                      {canApprove && article.status === 'pending_review' && (
                        <>
                          <button
                            type="button"
                            className="btn-primary text-xs"
                            disabled={reviewBusyId === article.id}
                            onClick={() => approveArticle(article.id)}
                          >
                            {t('articles.approve')}
                          </button>
                          <button
                            type="button"
                            className="btn-secondary text-xs"
                            disabled={reviewBusyId === article.id}
                            onClick={() => rejectArticle(article.id)}
                          >
                            {t('articles.rejectToDraft')}
                          </button>
                        </>
                      )}
                      {canDelete && (
                        <button
                          type="button"
                          className="btn-danger text-xs"
                          onClick={() => {
                            setDeleteError('');
                            setPendingDelete({ id: article.id, title: article.title });
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
        open={!!pendingDelete}
        title={t('common.confirmDelete')}
        message={pendingDelete ? t('articles.deleteConfirm', { title: pendingDelete.title }) : ''}
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
