import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Alert, ConfirmDialog, EmptyState, PageHeader, Spinner } from '../components/ui';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { articleService } from '../lib/services';
import { formatDate } from '../lib/format';

export function ArticlesManagePage() {
  const { t } = useTranslation();
  const { hasRole } = useAuth();
  const canDelete = hasRole('admin');
  const [pendingDelete, setPendingDelete] = useState(null);
  const [deleteError, setDeleteError] = useState('');
  const [deleting, setDeleting] = useState(false);

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

  if (isLoading) return <Spinner />;

  const articles = data ?? [];

  return (
    <div>
      <PageHeader
        title={t('articles.manageTitle')}
        subtitle={t('articles.manageSubtitle')}
      />
      <div className="mb-6 flex flex-wrap gap-3">
        <Link to="/articles/new" className="btn-primary">
          {t('articles.create')}
        </Link>
        <Link to="/categories/manage" className="btn-secondary">
          {t('categories.manageTitle')}
        </Link>
        <Link to="/articles" className="btn-secondary">
          {t('articles.viewPublic')}
        </Link>
      </div>

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

      {articles.length === 0 ? (
        <EmptyState>{t('articles.noArticlesManage')}</EmptyState>
      ) : (
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-slate-700 dark:bg-slate-800">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-gray-500 dark:bg-slate-700/50 dark:text-slate-400">
              <tr>
                <th className="px-4 py-3 font-medium">{t('articles.fieldTitle')}</th>
                <th className="px-4 py-3 font-medium">{t('articles.category')}</th>
                <th className="px-4 py-3 font-medium">{t('articles.fieldStatus')}</th>
                <th className="px-4 py-3 font-medium">{t('articles.updated')}</th>
                <th className="px-4 py-3 font-medium">{t('common.edit')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-slate-700">
              {articles.map((article) => (
                <tr key={article.id} className="dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-medium text-gray-900 dark:text-slate-100">{article.title}</td>
                  <td className="px-4 py-3 dark:text-slate-300">{article.category?.name ?? '—'}</td>
                  <td className="px-4 py-3 capitalize dark:text-slate-300">{article.status}</td>
                  <td className="px-4 py-3 dark:text-slate-400">{formatDate(article.updated_at)}</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      <Link to={`/articles/${article.id}/edit`} className="btn-secondary text-xs">
                        {t('common.edit')}
                      </Link>
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
