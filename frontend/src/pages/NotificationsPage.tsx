// @ts-nocheck
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Pagination } from '../components/Pagination';
import { EmptyState, PageHeader, Spinner } from '../components/ui';
import { Bell, Calendar, ChatBubble, FileText, Medal, Megaphone, Target } from '../components/Icons';
import { queryKeys } from '../lib/queryKeys';
import { notificationService } from '../lib/services';
import { formatDate } from '../lib/format';

const PAGE_SIZE = 20;

const TYPE_ICON_MAP = {
  new_content: FileText,
  quiz_result: Target,
  certificate: Medal,
  announcement: Megaphone,
  forum: ChatBubble,
  event_reminder: Calendar,
  event_registration: Calendar,
};

function NotificationIcon({ type }) {
  const Icon = TYPE_ICON_MAP[type] ?? Bell;
  return (
    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-ink-100 text-ink-700/80 dark:bg-slate-700 dark:text-slate-300">
      <Icon className="h-4 w-4" />
    </span>
  );
}

export function NotificationsPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.notifications({ page }),
    queryFn: async () => {
      const { data: res } = await notificationService.list({ page: String(page) });
      return res;
    },
  });

  const items = data?.results ?? [];
  const totalCount = data?.count ?? 0;
  const unread = items.filter((n) => !n.is_read).length;

  const markAll = useMutation({
    mutationFn: () => notificationService.markAllRead(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  });

  const markOne = useMutation({
    mutationFn: (id) => notificationService.markRead(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  });

  return (
    <div className="mx-auto max-w-2xl">
      <PageHeader
        title={`${t('notifications.title')}${unread ? ` (${unread} ${t('notifications.unread')})` : ''}`}
        action={
          unread > 0 && (
            <button
              type="button"
              className="btn-secondary"
              onClick={() => markAll.mutate()}
              disabled={markAll.isPending}
            >
              {t('notifications.markAllRead')}
            </button>
          )
        }
      />

      {isLoading ? (
        <Spinner />
      ) : items.length === 0 ? (
        <EmptyState>{t('notifications.empty')}</EmptyState>
      ) : (
        <>
          <div className="space-y-2">
            {items.map((n) => (
              <button
                key={n.id}
                type="button"
                onClick={() => !n.is_read && markOne.mutate(n.id)}
                className={`flex w-full items-start gap-3 rounded-xl border p-4 text-start transition-colors ${
                  n.is_read
                    ? 'border-ink-100 bg-white dark:border-slate-700 dark:bg-slate-800'
                    : 'border-brand-200 bg-brand-50 dark:border-brand-800 dark:bg-brand-950/30'
                }`}
              >
                <NotificationIcon type={n.notification_type} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-medium text-ink-900 dark:text-slate-100">{n.title}</p>
                    {!n.is_read && <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-brand-500" />}
                  </div>
                  <p className="mt-1 text-sm text-ink-700/80 dark:text-slate-400">{n.message}</p>
                  <p className="mt-1 text-xs text-ink-700/70 dark:text-slate-500">{formatDate(n.created_at)}</p>
                </div>
              </button>
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
