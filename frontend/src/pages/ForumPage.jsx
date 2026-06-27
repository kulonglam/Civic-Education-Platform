import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Pagination } from '../components/Pagination';
import { Alert, EmptyState, PageHeader, Spinner } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { forumService } from '../lib/services';
import { formatDate } from '../lib/format';

const PAGE_SIZE = 20;

const SORT_OPTIONS = [
  { value: '-created_at', labelKey: 'forum.sortNewest' },
  { value: 'created_at', labelKey: 'forum.sortOldest' },
  { value: '-comment_count', labelKey: 'forum.sortMostReplies' },
];

export function ForumPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [ordering, setOrdering] = useState('-created_at');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: '', content: '' });
  const [error, setError] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.forumTopics({ page, search, ordering }),
    queryFn: async () => {
      const params = { page: String(page), ordering };
      if (search) params.search = search;
      const { data: res } = await forumService.listTopics(params);
      return res;
    },
  });

  const topics = data?.results ?? [];
  const totalCount = data?.count ?? 0;

  const createTopic = useMutation({
    mutationFn: (payload) => forumService.createTopic(payload),
    onSuccess: () => {
      setForm({ title: '', content: '' });
      setShowForm(false);
      setError('');
      queryClient.invalidateQueries({ queryKey: ['forum', 'topics'] });
    },
    onError: (err) => setError(extractError(err)),
  });

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    setSearch(searchInput);
  };

  const handleSort = (val) => {
    setOrdering(val);
    setPage(1);
  };

  const submit = (e) => {
    e.preventDefault();
    createTopic.mutate(form);
  };

  return (
    <div>
      <PageHeader
        title={t('forum.title')}
        action={
          user && (
            <button type="button" className="btn-primary" onClick={() => setShowForm((s) => !s)}>
              {t('forum.newTopic')}
            </button>
          )
        }
      />

      {/* Search + Sort bar */}
      <div className="mb-5 flex flex-wrap gap-3">
        <form onSubmit={handleSearch} className="flex flex-1 gap-2">
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
        <form onSubmit={submit} className="card mb-6 space-y-4 dark:border-slate-700 dark:bg-slate-800">
          {error && <Alert>{error}</Alert>}
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
        <EmptyState>{search ? t('common.noResults') : t('forum.noTopics')}</EmptyState>
      ) : (
        <>
          <div className="space-y-3">
            {topics.map((topic) => (
              <Link
                key={topic.id}
                to={`/forum/${topic.id}`}
                className="card flex items-center justify-between transition-shadow hover:shadow-md dark:border-slate-700 dark:bg-slate-800 dark:hover:bg-slate-750"
              >
                <div className="min-w-0">
                  <h3 className="font-semibold text-gray-900 dark:text-slate-100">{topic.title}</h3>
                  <p className="mt-1 line-clamp-1 text-sm text-gray-500 dark:text-slate-400">{topic.content}</p>
                  <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-gray-400 dark:text-slate-500">
                    <span>{topic.author_name}</span>
                    <span>•</span>
                    <span>{formatDate(topic.created_at)}</span>
                    {!topic.is_approved && (
                      <span className="badge bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">
                        {t('forum.awaitingApproval')}
                      </span>
                    )}
                  </div>
                </div>
                <span className="ml-4 shrink-0 badge bg-gray-100 text-gray-600 dark:bg-slate-700 dark:text-slate-300">
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
