// @ts-nocheck
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Pagination } from '../components/Pagination';
import { EmptyState, PageHeader, Spinner } from '../components/ui';
import { BookmarkFilled } from '../components/Icons';
import { extractError } from '../lib/api';
import { formatDate } from '../lib/format';
import { queryKeys } from '../lib/queryKeys';
import { bookmarkService } from '../lib/services';

const PAGE_SIZE = 20;

export function SavedPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.bookmarks({ page }),
    queryFn: async () => {
      const { data: res } = await bookmarkService.list({ page: String(page) });
      return res;
    },
  });

  const remove = useMutation({
    mutationFn: (id) => bookmarkService.remove(id),
    onSuccess: () => {
      toast.success(t('saved.removed'));
      queryClient.invalidateQueries({ queryKey: queryKeys.bookmarks() });
    },
    onError: (err) => {
      toast.error(extractError(err));
    },
  });

  const items = data?.results ?? [];
  const totalCount = data?.count ?? 0;

  return (
    <div className="page-shell">
      <PageHeader
        eyebrow={t('nav.learn')}
        title={t('saved.title')}
        subtitle={t('saved.subtitle')}
      />

      {isLoading ? (
        <Spinner />
      ) : items.length === 0 ? (
        <EmptyState
          title={t('saved.empty')}
          action={
            <Link to="/articles" className="btn-primary">
              {t('saved.browse')}
            </Link>
          }
        >
          {t('saved.emptyHint')}
        </EmptyState>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((item) => {
              const isArticle = item.kind === 'article';
              const target = isArticle ? item.article : item.media;
              if (!target) return null;
              const href = isArticle ? `/articles/${target.id}` : `/media/${target.id}`;
              const kindLabel = isArticle ? t('saved.article') : t('saved.media');
              return (
                <article key={item.id} className="content-tile">
                  <div className="flex items-start justify-between gap-2">
                    <span className="badge bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
                      {kindLabel}
                    </span>
                    <BookmarkFilled className="h-4 w-4 text-brand-700 dark:text-brand-300" />
                  </div>
                  <h3 className="mt-3 font-display text-lg font-semibold text-ink-900 dark:text-slate-100">
                    <Link to={href} className="hover:underline">
                      {target.title}
                    </Link>
                  </h3>
                  <p className="content-meta mt-2">
                    {target.category_name || target.media_type || ''}
                    {target.published_at ? ` · ${formatDate(target.published_at)}` : ''}
                  </p>
                  <div className="mt-4 flex gap-2">
                    <Link to={href} className="btn-primary flex-1 text-center text-sm">
                      {t('common.readMore')}
                    </Link>
                    <button
                      type="button"
                      className="btn-secondary text-sm"
                      disabled={remove.isPending}
                      onClick={() => remove.mutate(item.id)}
                    >
                      {t('saved.remove')}
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
          <Pagination
            page={page}
            pageSize={PAGE_SIZE}
            totalCount={totalCount}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  );
}
