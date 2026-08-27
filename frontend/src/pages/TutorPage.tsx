import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useSearchParams } from 'react-router-dom';
import { Alert, EmptyState, PageHeader, Spinner } from '../components/ui';
import { AcademicCap, BookOpen } from '../components/Icons';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { formatDate } from '../lib/format';
import { localizedArticle } from '../lib/localizedContent';
import { streamTutorChat } from '../lib/tutorStream';
import { articleService, tutorService } from '../lib/services';
import { unwrapList } from '../types/api';
import type { TutorChatResponse, TutorMessage, TutorUsage } from '../types/api';
import { renderMarkdown } from '../lib/markdown';
import { VoiceInputButton } from '../components/VoiceInputButton';

function TutorBubble({ role, content }: { role: string; content: string }) {
  const isUser = role === 'user';
  const className = `max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
    isUser
      ? 'bg-brand-700 text-white shadow-soft whitespace-pre-wrap'
      : 'tutor-reply prose prose-sm max-w-none bg-ink-50 text-ink-900 dark:bg-slate-800 dark:text-slate-100 dark:prose-invert'
  }`;
  if (isUser) {
    return <div className={className}>{content}</div>;
  }
  return <div className={className} dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }} />;
}

function UsageMeter({ usage }: { usage: TutorUsage | undefined }) {
  const { t } = useTranslation();
  if (!usage) return null;

  const { daily_limit, messages_used_today, messages_remaining } = usage;
  const unlimited = daily_limit == null;
  const pct =
    unlimited || !daily_limit
      ? 0
      : Math.min(100, Math.round(((messages_used_today as number) / daily_limit) * 100));

  return (
    <div className="mb-4">
      <p className="text-sm text-ink-700/70 dark:text-slate-400">
        {unlimited
          ? t('tutor.usageUnlimited', { used: messages_used_today })
          : t('tutor.usageLimited', {
              used: messages_used_today,
              limit: daily_limit,
              remaining: messages_remaining,
            })}
      </p>
      {!unlimited && (
        <div
          className="mt-2 h-1.5 overflow-hidden rounded-full bg-ink-100 dark:bg-slate-700"
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          <div
            className="h-full rounded-full bg-brand-600 transition-all duration-500"
            style={{ width: `${pct}%` }}
          />
        </div>
      )}
    </div>
  );
}

function TutorSources({
  sources,
}: {
  sources?: Array<{ title?: string; url?: string; article_id?: string; source?: string; category?: string; excerpt?: string }>;
}) {
  const { t } = useTranslation();
  if (!sources?.length) return null;

  return (
    <div className="mt-2 max-w-[85%] rounded-xl border border-brand-200/80 bg-brand-50/80 px-3 py-2.5 text-xs dark:border-brand-800/50 dark:bg-brand-950/40">
      <p className="mb-1.5 flex items-center gap-1.5 font-semibold text-brand-900 dark:text-brand-200">
        <BookOpen className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
        {t('tutor.sources')}
      </p>
      <ul className="space-y-2">
        {sources.map((source: { title?: string; url?: string; article_id?: string; source?: string; category?: string; excerpt?: string }) => (
          <li key={`${source.article_id}-${source.source}`}>
            {source.article_id ? (
              <Link
                to={`/articles/${source.article_id}`}
                className="inline-flex items-center gap-1 font-medium text-brand-700 hover:underline dark:text-brand-300"
              >
                {source.title || source.source}
                <span aria-hidden="true">→</span>
              </Link>
            ) : (
              <span className="font-medium text-ink-800 dark:text-slate-200">
                {source.title || source.source}
              </span>
            )}
            {source.category && (
              <span className="ml-1 text-ink-700/60 dark:text-slate-400">· {source.category}</span>
            )}
            {source.excerpt && (
              <p className="mt-0.5 line-clamp-2 text-ink-700/70 dark:text-slate-400">{source.excerpt}</p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function TutorPage() {
  const { t, i18n } = useTranslation();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const articleId = searchParams.get('article') || undefined;
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<TutorMessage[]>([]);
  const [streamText, setStreamText] = useState('');
  const streamAbortRef = useRef<AbortController | null>(null);
  const [viewingHistory, setViewingHistory] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [error, setError] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const restoredRef = useRef(false);

  const { data: usage, isLoading: usageLoading } = useQuery({
    queryKey: queryKeys.tutorUsage,
    queryFn: async () => {
      const { data } = await tutorService.usage();
      return data;
    },
  });

  const { data: contextArticle } = useQuery({
    queryKey: queryKeys.article(articleId),
    queryFn: async () => {
      const { data } = await articleService.get(articleId);
      return data;
    },
    enabled: Boolean(articleId),
  });

  const contextArticleTitle = contextArticle
    ? localizedArticle(contextArticle, i18n.language).title
    : '';

  const { data: history = [] } = useQuery({
    queryKey: queryKeys.tutorHistory,
    queryFn: async () => {
      const { data } = await tutorService.history();
      return unwrapList(data);
    },
  });

  useEffect(() => {
    if (restoredRef.current) return;
    restoredRef.current = true;
    tutorService
      .getSession()
      .then(({ data }) => {
        if (data.messages?.length) {
          setMessages(data.messages);
          setViewingHistory(false);
        }
      })
      .catch(() => {});
  }, []);

  const loadHistorySession = useMutation({
    mutationFn: (sessionId: string) => tutorService.historyDetail(sessionId),
    onSuccess: ({ data }) => {
      setMessages(data.messages ?? []);
      setViewingHistory(true);
      setHistoryOpen(false);
      setError('');
    },
    onError: (err) => setError(extractError(err)),
  });

  const sendMessage = useMutation({
    mutationFn: async (message: string) => {
      setStreamText('');
      streamAbortRef.current?.abort();
      const controller = new AbortController();
      streamAbortRef.current = controller;

      return new Promise<{
        message: string;
        data: TutorChatResponse;
        streamed: boolean;
        reply?: string;
      }>((resolve, reject) => {
        let accumulated = '';
        streamTutorChat(message, {
          articleId,
          signal: controller.signal,
          onToken: (token) => {
            accumulated += token;
            setStreamText(accumulated);
          },
          onDone: (payload) =>
            resolve({
              message,
              data: {
                reply: accumulated || payload?.reply || '',
                sources: payload?.sources,
              },
              streamed: true,
              reply: accumulated || payload?.reply || '',
            }),
          onError: async (err) => {
            if (controller.signal.aborted) {
              reject(err);
              return;
            }
            try {
              const { data } = await tutorService.chat(message, articleId);
              resolve({ message, data, streamed: false });
            } catch (fallbackErr) {
              reject(fallbackErr);
            }
          },
        });
      });
    },
    onMutate: (message) => {
      setViewingHistory(false);
      setMessages((prev) => [...prev, { role: 'user', content: message }]);
      setInput('');
    },
    onSuccess: ({ data, streamed, reply }) => {
      setStreamText('');
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: (streamed ? reply : data.reply) ?? '',
          sources: data.sources ?? [],
        },
      ]);
      setError('');
      queryClient.invalidateQueries({ queryKey: queryKeys.tutorHistory });
      queryClient.setQueryData(queryKeys.tutorUsage, (old: TutorUsage | undefined) =>
        old
          ? {
              ...old,
              messages_used_today: data.messages_used_today,
              messages_remaining: data.messages_remaining,
              session_message_count: (old.session_message_count ?? 0) + 1,
            }
          : old
      );
      inputRef.current?.focus();
    },
    onError: (err) => {
      setStreamText('');
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last?.role === 'user') return prev.slice(0, -1);
        return prev;
      });
      setError(extractError(err));
    },
  });

  const clearSession = useMutation({
    mutationFn: () => tutorService.clearSession(),
    onSuccess: () => {
      setMessages([]);
      setViewingHistory(false);
      setError('');
      queryClient.invalidateQueries({ queryKey: queryKeys.tutorUsage });
    },
    onError: (err) => setError(extractError(err)),
  });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sendMessage.isPending, streamText]);

  useEffect(() => () => streamAbortRef.current?.abort(), []);

  const atLimit = usage?.daily_limit != null && usage.messages_remaining === 0;

  if (usageLoading) return <Spinner />;

  return (
    <div
      className="mx-auto flex max-w-3xl flex-col"
      style={{ minHeight: 'calc(100vh - 12rem)' }}
    >
      <PageHeader
        title={t('tutor.title')}
        subtitle={t('tutor.subtitle')}
        action={
          <div className="flex flex-wrap gap-2">
            {history.length > 0 && (
              <button
                type="button"
                className="btn-secondary text-sm"
                onClick={() => setHistoryOpen((open) => !open)}
              >
                {t('tutor.history')}
              </button>
            )}
            {messages.length > 0 && (
              <button
                type="button"
                className="btn-secondary text-sm"
                disabled={clearSession.isPending}
                onClick={() => clearSession.mutate()}
              >
                {t('tutor.clearSession')}
              </button>
            )}
          </div>
        }
      />

      <UsageMeter usage={usage} />

      {historyOpen && history.length > 0 && (
        <div className="surface mb-4 max-h-56 overflow-y-auto p-3">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-700/60 dark:text-slate-400">
            {t('tutor.recentChats')}
          </p>
          <ul className="space-y-2">
            {history.map((session) => (
              <li key={session.session_id ?? session.id}>
                <button
                  type="button"
                  className="w-full rounded-lg border border-ink-100 px-3 py-2 text-left text-sm transition-colors hover:border-brand-200 hover:bg-brand-50/50 dark:border-slate-700 dark:hover:bg-slate-800"
                  disabled={loadHistorySession.isPending}
                  onClick={() => loadHistorySession.mutate(session.session_id ?? session.id)}
                >
                  <span className="line-clamp-2 font-medium text-ink-900 dark:text-slate-100">
                    {session.preview || t('tutor.untitledChat')}
                  </span>
                  <span className="mt-1 block text-xs text-ink-700/55 dark:text-slate-400">
                    {t('tutor.turnCount', { count: session.turns })}
                    {session.last_at ? ` · ${formatDate(session.last_at)}` : ''}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mb-4">
        <Alert kind="info">{t('tutor.constitutionHint')}</Alert>
      </div>

      {articleId && (
        <div className="mb-4">
          <Alert kind="info">
            {contextArticleTitle
              ? t('tutor.articleContextNamed', { title: contextArticleTitle })
              : t('tutor.articleContext')}{' '}
            <Link to={`/articles/${articleId}`} className="font-semibold underline">
              {t('tutor.viewArticle')}
            </Link>
          </Alert>
        </div>
      )}

      {viewingHistory && (
        <div className="mb-4">
          <Alert kind="warning">{t('tutor.viewingHistory')}</Alert>
        </div>
      )}

      {error && (
        <div className="mb-4">
          <Alert>{error}</Alert>
        </div>
      )}

      {atLimit && (
        <div className="mb-4">
          <Alert kind="warning">{t('tutor.limitReached')}</Alert>
        </div>
      )}

      <div className="surface mb-4 flex flex-1 flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto p-5 sm:p-6">
          {messages.length === 0 ? (
            <EmptyState
              title={t('tutor.title')}
              icon={
                <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-100 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
                  <AcademicCap className="h-7 w-7" />
                </div>
              }
            >
              {t('tutor.emptyState')}
            </EmptyState>
          ) : (
            <div className="space-y-4">
              {messages.map((msg, index) => (
                <div
                  key={`${msg.role}-${index}`}
                  className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                >
                  <TutorBubble role={msg.role} content={msg.content} />
                  {msg.role === 'assistant' && <TutorSources sources={msg.sources} />}
                </div>
              ))}
              {sendMessage.isPending && streamText && (
                <div className="flex justify-start">
                  <TutorBubble role="assistant" content={streamText} />
                </div>
              )}
              {sendMessage.isPending && !streamText && (
                <div className="flex justify-start">
                  <div className="rounded-2xl bg-ink-50 px-4 py-3 text-sm text-ink-700/60 dark:bg-slate-800 dark:text-slate-400">
                    <span className="inline-flex gap-1">
                      <span className="animate-soft-pulse">●</span>
                      <span className="animate-soft-pulse [animation-delay:0.2s]">●</span>
                      <span className="animate-soft-pulse [animation-delay:0.4s]">●</span>
                    </span>
                    <span className="sr-only">{t('tutor.thinking')}</span>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        <form
          className="flex gap-2 border-t border-ink-100 bg-white/80 p-4 dark:border-slate-700 dark:bg-slate-900/50"
          onSubmit={(e) => {
            e.preventDefault();
            const text = input.trim();
            if (!text || sendMessage.isPending || atLimit) return;
            sendMessage.mutate(text);
          }}
        >
          <textarea
            ref={inputRef}
            className="input min-h-[52px] flex-1 resize-none py-3"
            rows={2}
            placeholder={t('tutor.placeholder')}
            value={input}
            disabled={sendMessage.isPending || atLimit}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                e.currentTarget.form?.requestSubmit();
              }
            }}
          />
          <VoiceInputButton
            disabled={sendMessage.isPending || atLimit}
            onTranscript={(text) => setInput((prev) => (prev ? `${prev} ${text}` : text))}
          />
          <button
            type="submit"
            className="btn-primary self-end px-5"
            disabled={!input.trim() || sendMessage.isPending || atLimit}
          >
            {sendMessage.isPending ? t('common.loading') : t('tutor.send')}
          </button>
        </form>
      </div>
    </div>
  );
}
