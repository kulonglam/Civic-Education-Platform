import { useEffect, useState, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { Breadcrumb } from '../components/Breadcrumb';
import { GuestSaveCta } from '../components/GuestSaveCta';
import { ReadAloudButton } from '../components/ReadAloudButton';
import { Alert, Spinner } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import { extractError } from '../lib/api';
import { formatDate } from '../lib/format';
import { forumService } from '../lib/services';
import type { ForumComment, Id } from '../types/api';

const REPORT_REASONS = [
  'hate_speech',
  'harassment',
  'misinformation',
  'political_manipulation',
  'other',
];

function ReportForm({
  onSubmit,
  submitting,
}: {
  onSubmit: (payload: { reason: string; details: string }) => void;
  submitting: boolean;
}) {
  const { t } = useTranslation();
  const [reason, setReason] = useState('misinformation');
  const [details, setDetails] = useState('');

  const submit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit({ reason, details });
  };

  return (
    <form onSubmit={submit} className="mt-3 space-y-2">
      <label className="block">
        <span className="label">{t('forum.reportReason')}</span>
        <select className="input mt-1" value={reason} onChange={(e) => setReason(e.target.value)}>
          {REPORT_REASONS.map((value) => (
            <option key={value} value={value}>{t(`forum.reason_${value}`)}</option>
          ))}
        </select>
      </label>
      <textarea
        className="input min-h-[72px]"
        placeholder={t('forum.reportDetails')}
        value={details}
        onChange={(e) => setDetails(e.target.value)}
      />
      <button type="submit" className="btn-secondary text-sm" disabled={submitting}>
        {t('forum.report')}
      </button>
    </form>
  );
}

function TopicDetailPage() {
  const { t } = useTranslation();
  const { id } = useParams();
  const { user, hasRole } = useAuth();
  const { isOrgModerator } = useOrganization();
  const [topic, setTopic] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [comment, setComment] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [reporting, setReporting] = useState('');

  const canModerate = hasRole('admin', 'moderator') || isOrgModerator;
  const isAuthor = Boolean(user && topic && String(topic.author) === String(user.id));

  const load = () => {
    if (!id) return;
    forumService
      .getTopic(id)
      .then((r) => setTopic(r.data))
      .catch(() => setError(t('common.noResults')))
      .finally(() => setLoading(false));
  };

  useEffect(load, [id, t]);

  const submit = async (e: FormEvent) => {
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

  const acceptAnswer = async (commentId: Id) => {
    if (!id) return;
    try {
      const { data } = await forumService.acceptAnswer(id, commentId);
      setTopic(data);
      setNotice(t('forum.answerAccepted'));
    } catch (err) {
      setError(extractError(err));
    }
  };

  const toggleLock = async () => {
    if (!id || !topic) return;
    try {
      const { data } = await forumService.lockTopic(id, !topic.is_locked);
      setTopic((current: { comments?: ForumComment[] } | null) => ({
        ...current,
        ...data,
        comments: current?.comments ?? [],
      }));
    } catch (err) {
      setError(extractError(err));
    }
  };

  const reportTopic = async (payload: { reason: string; details: string }) => {
    if (!id) return;
    setReporting('topic');
    setError('');
    try {
      await forumService.reportTopic(id, payload);
      setNotice(t('forum.reportSubmitted'));
    } catch (err) {
      setError(extractError(err));
    } finally {
      setReporting('');
    }
  };

  const reportComment = async (commentId: Id, payload: { reason: string; details: string }) => {
    setReporting(commentId);
    setError('');
    try {
      await forumService.reportComment(commentId, payload);
      setNotice(t('forum.reportSubmitted'));
    } catch (err) {
      setError(extractError(err));
    } finally {
      setReporting('');
    }
  };

  if (loading) return <Spinner />;
  if (!topic) return <Alert>{error || t('common.noResults')}</Alert>;

  const visibleComments = (topic.comments ?? []).filter((c: ForumComment) => c.is_approved || canModerate);
  const sortedComments = [...visibleComments].sort(
    (a: ForumComment & { is_expert?: boolean }, b: ForumComment & { is_expert?: boolean }) => {
    const aAccepted = topic.accepted_answer_id === a.id ? 0 : 1;
    const bAccepted = topic.accepted_answer_id === b.id ? 0 : 1;
    if (aAccepted !== bAccepted) return aAccepted - bAccepted;
    const aExpert = a.is_expert ? 0 : 1;
    const bExpert = b.is_expert ? 0 : 1;
    return aExpert - bExpert;
  });
  const approvedCount = (topic.comments ?? []).filter((c: ForumComment) => c.is_approved).length;
  const canReply = Boolean(user) && !topic.is_locked;

  return (
    <div className="mx-auto max-w-3xl">
      <Breadcrumb
        items={[
          { to: '/forum', label: t('forum.title') },
          { label: topic.title },
        ]}
      />

      <div className="card dark:border-slate-700 dark:bg-slate-800">
        <div className="mb-3 flex flex-wrap gap-2">
          <span className="badge bg-ink-100 text-ink-700 dark:bg-slate-700 dark:text-slate-300">
            {t(`forum.kind_${topic.kind || 'discussion'}`)}
          </span>
          <span className="badge bg-brand-50 text-brand-800 dark:bg-brand-900/30 dark:text-brand-200">
            {t(`forum.board_${topic.board || 'general'}`)}
          </span>
          {topic.is_locked && (
            <span className="badge bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300">
              {t('forum.locked')}
            </span>
          )}
        </div>
        <h1 className="text-2xl font-bold text-ink-900 dark:text-slate-100">{topic.title}</h1>
        <div className="mt-3">
          <ReadAloudButton text={`${topic.title}. ${topic.content || ''}`} />
        </div>
        <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-ink-700/60 dark:text-slate-400">
          <span>{topic.author_name}</span>
          <span>•</span>
          <span>{formatDate(topic.created_at)}</span>
        </div>
        <p className="mt-4 whitespace-pre-wrap text-ink-800 dark:text-slate-300">{topic.content}</p>
        {topic.is_locked && (
          <p className="mt-4 text-sm text-rose-700 dark:text-rose-300">{t('forum.lockedNotice')}</p>
        )}
        {canModerate && (
          <button type="button" className="btn-secondary mt-4 text-sm" onClick={toggleLock}>
            {topic.is_locked ? t('forum.unlockTopic') : t('forum.lockTopic')}
          </button>
        )}
        {user && (
          <ReportForm onSubmit={reportTopic} submitting={reporting === 'topic'} />
        )}
      </div>

      {notice && (
        <div className="mt-4">
          <Alert kind="success">{notice}</Alert>
        </div>
      )}
      {error && (
        <div className="mt-4">
          <Alert>{error}</Alert>
        </div>
      )}

      <h2 className="mb-3 mt-8 text-lg font-semibold text-ink-900 dark:text-slate-100">
        {t('forum.comments')} ({approvedCount})
      </h2>

      <div className="space-y-3">
        {sortedComments.map((c: ForumComment & { is_expert?: boolean }) => {
          const accepted = topic.accepted_answer_id === c.id;
          return (
            <div
              key={c.id}
              className={`card dark:border-slate-700 dark:bg-slate-800 ${
                accepted ? 'border-brand-300 dark:border-brand-700' : ''
              }`}
            >
              <div className="flex flex-wrap items-center gap-2 text-sm font-medium text-ink-700 dark:text-slate-300">
                {c.author_name}
                {c.is_expert && (
                  <span className="badge bg-brand-100 text-brand-800 dark:bg-brand-900/40 dark:text-brand-200">
                    {t('forum.expertReply')}
                  </span>
                )}
                {accepted && (
                  <span className="badge bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-200">
                    {t('forum.acceptedAnswer')}
                  </span>
                )}
                {!c.is_approved && (
                  <span className="badge bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">
                    {t('forum.awaitingApproval')}
                  </span>
                )}
                <span className="text-xs font-normal text-ink-700/70 dark:text-slate-500">
                  {formatDate(c.created_at)}
                </span>
              </div>
              <p className="mt-2 whitespace-pre-wrap text-sm text-ink-700 dark:text-slate-300">{c.comment}</p>
              {topic.kind === 'question' && c.is_approved && (isAuthor || canModerate) && !accepted && (
                <button
                  type="button"
                  className="btn-secondary mt-3 text-sm"
                  onClick={() => acceptAnswer(c.id)}
                >
                  {t('forum.acceptAnswer')}
                </button>
              )}
              {user && (
                <ReportForm
                  onSubmit={(payload: { reason: string; details: string }) => reportComment(c.id, payload)}
                  submitting={reporting === c.id}
                />
              )}
            </div>
          );
        })}
      </div>

      {canReply ? (
        <form onSubmit={submit} className="card mt-6 space-y-3 dark:border-slate-700 dark:bg-slate-800">
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
          <p className="text-xs text-ink-700/70 dark:text-slate-500">{t('forum.awaitingApproval')}</p>
        </form>
      ) : user ? (
        <p className="mt-6 text-sm text-ink-700/70 dark:text-slate-400">{t('forum.lockedNotice')}</p>
      ) : (
        <GuestSaveCta className="mt-6" />
      )}
    </div>
  );
}

export { TopicDetailPage };
