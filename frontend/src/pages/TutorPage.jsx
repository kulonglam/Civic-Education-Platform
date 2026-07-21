import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSearchParams } from 'react-router-dom';
import { Alert, EmptyState, PageHeader, Spinner } from '../components/ui';
import { AcademicCap } from '../components/Icons';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { tutorService } from '../lib/services';

function UsageMeter({ usage }) {
  const { t } = useTranslation();
  if (!usage) return null;

  const { daily_limit, messages_used_today, messages_remaining } = usage;
  const unlimited = daily_limit == null;
  const pct =
    unlimited || !daily_limit
      ? 0
      : Math.min(100, Math.round((messages_used_today / daily_limit) * 100));

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

export function TutorPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const articleId = searchParams.get('article') || undefined;
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState('');
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  const { data: usage, isLoading: usageLoading } = useQuery({
    queryKey: queryKeys.tutorUsage,
    queryFn: async () => {
      const { data } = await tutorService.usage();
      return data;
    },
  });

  const sendMessage = useMutation({
    mutationFn: (message) => tutorService.chat(message, articleId),
    onSuccess: ({ data }, message) => {
      setMessages((prev) => [
        ...prev,
        { role: 'user', content: message },
        { role: 'assistant', content: data.reply },
      ]);
      setInput('');
      setError('');
      queryClient.setQueryData(queryKeys.tutorUsage, (old) =>
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
    onError: (err) => setError(extractError(err)),
  });

  const clearSession = useMutation({
    mutationFn: () => tutorService.clearSession(),
    onSuccess: () => {
      setMessages([]);
      setError('');
      queryClient.invalidateQueries({ queryKey: queryKeys.tutorUsage });
    },
    onError: (err) => setError(extractError(err)),
  });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sendMessage.isPending]);

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
          messages.length > 0 ? (
            <button
              type="button"
              className="btn-secondary text-sm"
              disabled={clearSession.isPending}
              onClick={() => clearSession.mutate()}
            >
              {t('tutor.clearSession')}
            </button>
          ) : null
        }
      />

      <UsageMeter usage={usage} />

      <div className="mb-4">
        <Alert kind="info">{t('tutor.constitutionHint')}</Alert>
      </div>

      {articleId && (
        <div className="mb-4">
          <Alert kind="info">{t('tutor.articleContext')}</Alert>
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
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                      msg.role === 'user'
                        ? 'bg-brand-700 text-white shadow-soft'
                        : 'bg-ink-50 text-ink-900 dark:bg-slate-800 dark:text-slate-100'
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
              {sendMessage.isPending && (
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
