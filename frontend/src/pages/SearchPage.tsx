import { useQuery } from '@tanstack/react-query';
import { useEffect, useState, type ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useSearchParams } from 'react-router-dom';
import { Alert, EmptyState, PageHeader, Spinner } from '../components/ui';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { formatDate } from '../lib/format';
import { searchService } from '../lib/services';
import { VoiceInputButton } from '../components/VoiceInputButton';

function ResultSection({ title, children, emptyLabel }: { title: string; children: ReactNode; emptyLabel: string }) {
  return (
    <section className="mb-8">
      <h2 className="mb-3 font-display text-lg font-semibold text-ink-900 dark:text-slate-100">{title}</h2>
      {children ?? (
        <p className="text-sm text-ink-700/60 dark:text-slate-400">{emptyLabel}</p>
      )}
    </section>
  );
}

export function SearchPage() {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(() => searchParams.get('q') || '');
  const debouncedQuery = useDebouncedValue(query, 300);

  useEffect(() => {
    const next = debouncedQuery.trim();
    if (next) {
      setSearchParams({ q: next }, { replace: true });
    } else {
      setSearchParams({}, { replace: true });
    }
  }, [debouncedQuery, setSearchParams]);

  const { data, isLoading, error, isFetching } = useQuery({
    queryKey: queryKeys.search(debouncedQuery.trim()),
    queryFn: async () => {
      const { data: res } = await searchService.query(debouncedQuery.trim());
      return res;
    },
    enabled: debouncedQuery.trim().length >= 2,
  });

  const hasQuery = debouncedQuery.trim().length >= 2;
  const totalResults = hasQuery
    ? (data?.articles?.length ?? 0) + (data?.media?.length ?? 0) + (data?.topics?.length ?? 0)
    : 0;

  return (
    <div className="page-shell mx-auto max-w-3xl">
      <PageHeader title={t('search.title')} subtitle={t('search.subtitle')} />

      <form
        className="mb-8"
        onSubmit={(e) => {
          e.preventDefault();
        }}
      >
        <label className="sr-only" htmlFor="global-search">
          {t('search.placeholder')}
        </label>
        <div className="flex flex-wrap gap-2">
          <input
            id="global-search"
            type="search"
            className="input min-w-0 flex-1"
            placeholder={t('search.placeholder')}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
          />
          <VoiceInputButton onTranscript={(text) => setQuery((prev) => (prev ? `${prev} ${text}` : text))} />
        </div>
        <p className="mt-2 text-xs text-ink-700/55 dark:text-slate-400">{t('search.hint')}</p>
      </form>

      {!hasQuery && (
        <EmptyState title={t('search.title')}>{t('search.startTyping')}</EmptyState>
      )}

      {hasQuery && isLoading && <Spinner />}

      {error && (
        <Alert>{extractError(error)}</Alert>
      )}

      {hasQuery && !isLoading && !error && totalResults === 0 && (
        <EmptyState title={t('search.noResults', { query: debouncedQuery.trim() })}>
          {t('search.tryDifferent')}
        </EmptyState>
      )}

      {hasQuery && data && totalResults > 0 && (
        <div className={isFetching ? 'opacity-70 transition-opacity' : ''}>
          <ResultSection
            title={t('search.articles')}
            emptyLabel={t('search.noneArticles')}
          >
            {data.articles?.length ? (
              <ul className="space-y-2">
                {data.articles.map((item) => (
                  <li key={item.id}>
                    <Link
                      to={`/articles/${item.id}`}
                      className="block rounded-xl border border-ink-100 bg-white/80 px-4 py-3 transition-colors hover:border-brand-200 dark:border-slate-700 dark:bg-slate-900/50"
                    >
                      <p className="font-medium text-ink-900 dark:text-slate-100">{item.title}</p>
                      <p className="mt-1 text-xs text-ink-700/60 dark:text-slate-400">
                        {typeof item.category === 'string' ? item.category : item.category?.name || t('articles.title')}
                        {item.published_at ? ` · ${formatDate(item.published_at)}` : ''}
                      </p>
                    </Link>
                  </li>
                ))}
              </ul>
            ) : null}
          </ResultSection>

          <ResultSection title={t('search.media')} emptyLabel={t('search.noneMedia')}>
            {data.media?.length ? (
              <ul className="space-y-2">
                {data.media.map((item) => (
                  <li key={item.id}>
                    <Link
                      to={`/media/${item.id}`}
                      className="block rounded-xl border border-ink-100 bg-white/80 px-4 py-3 transition-colors hover:border-brand-200 dark:border-slate-700 dark:bg-slate-900/50"
                    >
                      <p className="font-medium text-ink-900 dark:text-slate-100">{item.title}</p>
                      <p className="mt-1 text-xs text-ink-700/60 dark:text-slate-400">
                        {item.media_type === 'audio' ? t('media.typeAudio') : t('media.typeVideo')}
                        {item.category ? ` · ${item.category}` : ''}
                      </p>
                    </Link>
                  </li>
                ))}
              </ul>
            ) : null}
          </ResultSection>

          <ResultSection title={t('search.forum')} emptyLabel={t('search.noneForum')}>
            {data.topics?.length ? (
              <ul className="space-y-2">
                {data.topics.map((item) => (
                  <li key={item.id}>
                    <Link
                      to={`/forum/${item.id}`}
                      className="block rounded-xl border border-ink-100 bg-white/80 px-4 py-3 transition-colors hover:border-brand-200 dark:border-slate-700 dark:bg-slate-900/50"
                    >
                      <p className="font-medium text-ink-900 dark:text-slate-100">{item.title}</p>
                      {item.created_at && (
                        <p className="mt-1 text-xs text-ink-700/60 dark:text-slate-400">
                          {formatDate(item.created_at)}
                        </p>
                      )}
                    </Link>
                  </li>
                ))}
              </ul>
            ) : null}
          </ResultSection>
        </div>
      )}
    </div>
  );
}
