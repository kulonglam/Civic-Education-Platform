import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Pagination } from '../components/Pagination';
import { Alert, EmptyState, PageHeader, Spinner } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { engagementService, forumService } from '../lib/services';
import type { ForumTopicWrite } from '../types/api';
import { formatDate } from '../lib/format';

const PAGE_SIZE = 20;

const SORT_OPTIONS = [
  { value: '-created_at', labelKey: 'forum.sortNewest' },
  { value: 'created_at', labelKey: 'forum.sortOldest' },
  { value: '-comment_count', labelKey: 'forum.sortMostReplies' },
];

const KIND_FILTERS = ['', 'discussion', 'question'];
const BOARD_FILTERS = ['', 'general', 'constitution', 'elections', 'rights', 'governance', 'media', 'peace'];

export function ForumPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [ordering, setOrdering] = useState('-created_at');
  const [kind, setKind] = useState('');
  const [board, setBoard] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: '', content: '', kind: 'discussion', board: 'general' });
  const [error, setError] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.forumTopics({ page, search, ordering, kind, board }),
    queryFn: async () => {
      const params: Record<string, string> = { page: String(page), ordering };
      if (search) params.search = search;
      if (kind) params.kind = kind;
      if (board) params.board = board;
      const { data: res } = await forumService.listTopics(params);
      return res;
    },
  });

  const { data: polls = [] } = useQuery({
    queryKey: queryKeys.engagementPolls(),
    enabled: Boolean(user),
    queryFn: async () => {
      const { data: res } = await engagementService.polls();
      return res.results ?? res ?? [];
    },
  });

  const topics = data?.results ?? [];
  const totalCount = data?.count ?? 0;

  const createTopic = useMutation({
    mutationFn: (payload: ForumTopicWrite) => forumService.createTopic(payload),
    onSuccess: () => {
      setForm({ title: '', content: '', kind: 'discussion', board: 'general' });
      setShowForm(false);
      setError('');
      queryClient.invalidateQueries({ queryKey: ['forum', 'topics'] });
    },
    onError: (err) => setError(extractError(err)),
  });

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    setPage(1);
    setSearch(searchInput);
  };

  const handleSort = (val: string) => {
    setOrdering(val);
    setPage(1);
  };

  const submit = (e: FormEvent) => {
    e.preventDefault();
    createTopic.mutate(form);
  };

  return (
    <div className="page-shell">
      <PageHeader
        eyebrow={t('nav.learn')}
        title={t('forum.title')}
        action={
          user && (
            <button type="button" className="btn-primary" onClick={() => setShowForm((s) => !s)}>
              {t('forum.newTopic')}
            </button>
          )
        }
      />

      <div className="card mb-6 border-amber-200 bg-amber-50 dark:border-amber-900/40 dark:bg-amber-950/20">
        <h2 className="font-display text-base font-semibold text-ink-900 dark:text-slate-100">
          {t('forum.guidelinesTitle')}
        </h2>
        <p className="mt-2 text-sm leading-relaxed text-ink-700 dark:text-slate-300">
          {t('forum.guidelinesBody')}
        </p>
      </div>

      {user && polls.length > 0 && (
        <section className="card mb-6">
          <div className="mb-3 flex items-center justify-between gap-3">
            <h2 className="font-display text-base font-semibold text-ink-900 dark:text-slate-100">
              {t('forum.communityPolls')}
            </h2>
            <Link to="/engage" className="text-sm font-semibold text-brand-700 hover:underline dark:text-brand-300">
              {t('forum.voteOnEngage')}
            </Link>
          </div>
          <ul className="space-y-2">
            {polls.slice(0, 2).map((poll) => (
              <li key={poll.id} className="text-sm text-ink-800 dark:text-slate-200">
                {poll.question}
              </li>
            ))}
          </ul>
        </section>
      )}

      <div className="filter-bar flex flex-wrap gap-3">
        <form onSubmit={handleSearch} className="flex min-w-0 flex-1 gap-2">
          <input
            type="search"
            className="input min-w-0 flex-1"
            placeholder={t('forum.searchPlaceholder')}
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
          <button type="submit" className="btn-secondary shrink-0">
            {t('common.search')}
          </button>
          {search && (
            <button
              type="button"
              className="btn-secondary shrink-0"
              onClick={() => { setSearch(''); setSearchInput(''); setPage(1); }}
            >
              {t('common.clear')}
            </button>
          )}
        </form>
        <select
          className="input w-auto"
          value={kind}
          onChange={(e) => { setKind(e.target.value); setPage(1); }}
          aria-label={t('forum.kind')}
        >
          {KIND_FILTERS.map((value) => (
            <option key={value || 'all'} value={value}>
              {value ? t(`forum.kind_${value}`) : t('forum.allKinds')}
            </option>
          ))}
        </select>
        <select
          className="input w-auto"
          value={board}
          onChange={(e) => { setBoard(e.target.value); setPage(1); }}
          aria-label={t('forum.board')}
        >
          {BOARD_FILTERS.map((value) => (
            <option key={value || 'all'} value={value}>
              {value ? t(`forum.board_${value}`) : t('forum.allBoards')}
            </option>
          ))}
        </select>
        <select
          className="input w-auto"
          value={ordering}
          onChange={(e) => handleSort(e.target.value)}
          aria-label={t('forum.sortBy')}
        >
          {SORT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>{t(opt.labelKey)}</option>
          ))}
        </select>
      </div>

      {showForm && (
        <form onSubmit={submit} className="card space-y-4">
          {error && <Alert>{error}</Alert>}
          <p className="text-sm text-ink-700/80 dark:text-slate-400">{t('forum.preModerationNote')}</p>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label">{t('forum.kind')}</label>
              <select
                className="input"
                value={form.kind}
                onChange={(e) => setForm((f) => ({ ...f, kind: e.target.value }))}
              >
                <option value="discussion">{t('forum.kind_discussion')}</option>
                <option value="question">{t('forum.kind_question')}</option>
              </select>
            </div>
            <div>
              <label className="label">{t('forum.board')}</label>
              <select
                className="input"
                value={form.board}
                onChange={(e) => setForm((f) => ({ ...f, board: e.target.value }))}
              >
                {BOARD_FILTERS.filter(Boolean).map((value) => (
                  <option key={value} value={value}>{t(`forum.board_${value}`)}</option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="label">{t('forum.topicTitle')}</label>
            <input
              className="input"
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
              required
            />
          </div>
          <div>
            <label className="label">{t('forum.topicContent')}</label>
            <textarea
              className="input min-h-[120px]"
              value={form.content}
              onChange={(e) => setForm((f) => ({ ...f, content: e.target.value }))}
              required
            />
          </div>
          <div className="flex gap-2">
            <button type="submit" className="btn-primary" disabled={createTopic.isPending}>
              {t('forum.post')}
            </button>
            <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>
              {t('common.cancel')}
            </button>
          </div>
        </form>
      )}

      {isLoading ? (
        <Spinner />
      ) : topics.length === 0 ? (
        <EmptyState title={search || kind || board ? t('common.noResults') : t('forum.noTopics')}>
          {t('common.noResults')}
        </EmptyState>
      ) : (
        <>
          <div className="content-list">
            {topics.map((topic) => (
              <Link
                key={topic.id}
                to={`/forum/${topic.id}`}
                className="content-row flex items-center justify-between gap-4"
              >
                <div className="min-w-0">
                  <div className="mb-1 flex flex-wrap gap-2">
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
                  <h3 className="font-display text-base font-semibold text-ink-900 dark:text-slate-100">
                    {topic.title}
                  </h3>
                  <p className="mt-1 line-clamp-1 text-sm text-ink-700/65 dark:text-slate-400">
                    {topic.content}
                  </p>
                  <div className="content-meta">
                    <span>{topic.author_name}</span>
                    <span aria-hidden="true">·</span>
                    <span>{formatDate(topic.created_at)}</span>
                    {!topic.is_approved && (
                      <span className="badge bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">
                        {t('forum.awaitingApproval')}
                      </span>
                    )}
                  </div>
                </div>
                <span className="badge shrink-0 bg-ink-100 text-ink-700 dark:bg-slate-700 dark:text-slate-300">
                  {topic.comment_count} {t('forum.comments')}
                </span>
              </Link>
            ))}
          </div>
          <Pagination
            page={page}
            totalCount={totalCount}
            pageSize={PAGE_SIZE}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  );
}
