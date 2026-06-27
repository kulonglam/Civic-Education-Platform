import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { forumService } from '../lib/services';
import { useAuth } from '../context/AuthContext';
import { Alert, Spinner } from '../components/ui';
import { Breadcrumb } from '../components/Breadcrumb';
import { extractError } from '../lib/api';
import { formatDate } from '../lib/format';

function TopicDetailPage() {
  const { t } = useTranslation();
  const { id } = useParams();
  const { user } = useAuth();
  const [topic, setTopic] = useState(null);
  const [loading, setLoading] = useState(true);
  const [comment, setComment] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const load = () => {
    if (!id) return;
    forumService
      .getTopic(id)
      .then((r) => setTopic(r.data))
      .catch(() => setError(t('common.noResults')))
      .finally(() => setLoading(false));
  };

  useEffect(load, [id]);

  const submit = async (e) => {
    e.preventDefault();
    if (!id) return;
    setSubmitting(true);
    setError('');
    try {
      await forumService.addComment(id, comment);
      setComment('');
      load();
    } catch (err) {
      setError(extractError(err));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <Spinner />;
  if (!topic) return <Alert>{error || t('common.noResults')}</Alert>;

  const approvedComments = topic.comments.filter((c) => c.is_approved);

  return (
    <div className="mx-auto max-w-3xl">
      <Breadcrumb
        items={[
          { to: '/forum', label: t('forum.title') },
          { label: topic.title },
        ]}
      />

      <div className="card dark:border-slate-700 dark:bg-slate-800">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-slate-100">{topic.title}</h1>
        <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-gray-500 dark:text-slate-400">
          <span>{topic.author_name}</span>
          <span>•</span>
          <span>{formatDate(topic.created_at)}</span>
        </div>
        <p className="mt-4 whitespace-pre-wrap text-gray-800 dark:text-slate-300">{topic.content}</p>
      </div>

      <h2 className="mb-3 mt-8 text-lg font-semibold text-gray-900 dark:text-slate-100">
        {t('forum.comments')} ({approvedComments.length})
      </h2>

      <div className="space-y-3">
        {approvedComments.map((c) => (
          <div key={c.id} className="card dark:border-slate-700 dark:bg-slate-800">
            <div className="flex flex-wrap items-center gap-2 text-sm font-medium text-gray-700 dark:text-slate-300">
              {c.author_name}
              <span className="text-xs font-normal text-gray-400 dark:text-slate-500">
                {formatDate(c.created_at)}
              </span>
            </div>
            <p className="mt-2 whitespace-pre-wrap text-sm text-gray-700 dark:text-slate-300">{c.comment}</p>
          </div>
        ))}
      </div>

      {user ? (
        <form onSubmit={submit} className="card mt-6 space-y-3 dark:border-slate-700 dark:bg-slate-800">
          {error && <Alert>{error}</Alert>}
          <label className="label">{t('forum.addComment')}</label>
          <textarea
            className="input min-h-[100px]"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            required
          />
          <button type="submit" className="btn-primary" disabled={submitting}>
            {t('forum.reply')}
          </button>
          <p className="text-xs text-gray-400 dark:text-slate-500">{t('forum.awaitingApproval')}</p>
        </form>
      ) : (
        <div className="mt-6">
          <Link to="/login" className="btn-primary">
            {t('nav.login')}
          </Link>
        </div>
      )}
    </div>
  );
}

export { TopicDetailPage };
