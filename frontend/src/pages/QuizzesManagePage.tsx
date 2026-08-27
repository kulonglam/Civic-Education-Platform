import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Alert, ConfirmDialog, EmptyState, PageHeader, Spinner } from '../components/ui';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { quizService } from '../lib/services';

export function QuizzesManagePage() {
  const { t } = useTranslation();
  const { hasRole } = useAuth();
  const canDelete = hasRole('admin');
  const [pendingDelete, setPendingDelete] = useState(null);
  const [deleteError, setDeleteError] = useState('');
  const [deleting, setDeleting] = useState(false);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: queryKeys.quizzesManage,
    queryFn: async () => {
      const { data: res } = await quizService.list();
      return res.results ?? res;
    },
  });

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setDeleting(true);
    setDeleteError('');
    try {
      await quizService.remove(pendingDelete.id);
      setPendingDelete(null);
      await refetch();
    } catch (err) {
      setDeleteError(extractError(err));
    } finally {
      setDeleting(false);
    }
  };

  if (isLoading) return <Spinner />;

  const quizzes = data ?? [];

  return (
    <div>
      <PageHeader title={t('quizzes.manageTitle')} subtitle={t('quizzes.manageSubtitle')} />
      <div className="mb-6 flex flex-wrap gap-3">
        <Link to="/quizzes/new" className="btn-primary">
          {t('quizzes.create')}
        </Link>
        <Link to="/quizzes" className="btn-secondary">
          {t('quizzes.viewPublic')}
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

      {quizzes.length === 0 ? (
        <EmptyState>{t('quizzes.noQuizzesManage')}</EmptyState>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-ink-100 bg-white dark:border-slate-700 dark:bg-slate-800">
          <table className="min-w-full text-sm">
            <thead className="bg-ink-50 text-left text-ink-700/60 dark:bg-slate-700/50 dark:text-slate-400">
              <tr>
                <th className="px-4 py-3 font-medium">{t('quizzes.fieldTitle')}</th>
                <th className="px-4 py-3 font-medium">{t('quizzes.passingScore')}</th>
                <th className="px-4 py-3 font-medium">{t('quizzes.questions')}</th>
                <th className="px-4 py-3 font-medium">{t('quizzes.fieldActive')}</th>
                <th className="px-4 py-3 font-medium">{t('common.edit')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-100 dark:divide-slate-700">
              {quizzes.map((quiz) => (
                <tr key={quiz.id} className="dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-medium text-ink-900 dark:text-slate-100">{quiz.title}</td>
                  <td className="px-4 py-3 dark:text-slate-300">{quiz.passing_score}%</td>
                  <td className="px-4 py-3 dark:text-slate-300">{quiz.question_count ?? quiz.questions?.length ?? 0}</td>
                  <td className="px-4 py-3 dark:text-slate-300">{quiz.is_active ? t('common.approved') : t('common.pending')}</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      <Link to={`/quizzes/${quiz.id}/edit`} className="btn-secondary text-xs">
                        {t('common.edit')}
                      </Link>
                      {canDelete && (
                        <button
                          type="button"
                          className="btn-danger text-xs"
                          onClick={() => {
                            setDeleteError('');
                            setPendingDelete({ id: quiz.id, title: quiz.title });
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
        message={pendingDelete ? t('quizzes.deleteConfirm', { title: pendingDelete.title }) : ''}
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
