import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSearchParams } from 'react-router-dom';
import { Alert, PageHeader, Spinner } from '../components/ui';
import { AcademicCap } from '../components/Icons';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { tutorService } from '../lib/services';

function UsageMeter({ usage }) {
  const { t } = useTranslation();
  if (!usage) return null;

  const { daily_limit, messages_used_today, messages_remaining } = usage;
  const unlimited = daily_limit == null;

  return (
    <p className="text-sm text-gray-500 dark:text-slate-400">
      {unlimited
        ? t('tutor.usageUnlimited', { used: messages_used_today })
        : t('tutor.usageLimited', {
            used: messages_used_today,
            limit: daily_limit,
            remaining: messages_remaining,
          })}
    </p>
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
    <div className="mx-auto flex max-w-3xl flex-col" style={{ minHeight: 'calc(100vh - 12rem)' }}>
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

      {articleId && (
        <div className="mb-4 mt-2">
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

      <div className="card mb-4 flex-1 overflow-y-auto dark:border-slate-700">
        {messages.length === 0 ? (
          <div className="flex h-full min-h-[280px] flex-col items-center justify-center text-center text-gray-500 dark:text-slate-400">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-50 text-brand-600 dark:bg-brand-900/40 dark:text-brand-300">
              <AcademicCap className="h-7 w-7" />
            </div>
            <p className="mt-4 max-w-md text-sm">{t('tutor.emptyState')}</p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg, index) => (
              <div
                key={`${msg.role}-${index}`}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${
                    msg.role === 'user'
                      ? 'bg-brand-600 text-white'
                      : 'bg-gray-100 text-gray-800 dark:bg-slate-700 dark:text-slate-100'
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {sendMessage.isPending && (
              <div className="flex justify-start">
                <div className="rounded-2xl bg-gray-100 px-4 py-3 text-sm text-gray-500 dark:bg-slate-700 dark:text-slate-300">
                  {t('tutor.thinking')}
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <form
        className="flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          const text = input.trim();
          if (!text || sendMessage.isPending || atLimit) return;
          sendMessage.mutate(text);
        }}
      >
        <textarea
          className="input min-h-[48px] flex-1 resize-none py-3"
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
  );
}
