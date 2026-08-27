import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { Breadcrumb } from '../components/Breadcrumb';
import { EventKindBadge } from '../components/EventKindBadge';
import { GuestSaveCta } from '../components/GuestSaveCta';
import { Alert, Spinner } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import { extractError } from '../lib/api';
import { formatDate, formatDateTime } from '../lib/format';
import { localizedEvent } from '../lib/localizedContent';
import { renderMarkdown } from '../lib/markdown';
import { queryKeys } from '../lib/queryKeys';
import { eventsService } from '../lib/services';
import { ReadAloudButton } from '../components/ReadAloudButton';
import { WhatsAppShareButton } from '../components/WhatsAppShareButton';

async function downloadIcs(id, title) {
  const { data } = await eventsService.calendar(id);
  const blob = data instanceof Blob ? data : new Blob([data], { type: 'text/calendar' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${title || 'event'}.ics`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function EventsDetailPage() {
  const { t, i18n } = useTranslation();
  const { id } = useParams();
  const { user, hasRole } = useAuth();
  const { isOrgContentManager } = useOrganization();
  const canEdit = hasRole('admin', 'editor') || isOrgContentManager;
  const queryClient = useQueryClient();
  const [actionError, setActionError] = useState('');
  const [downloading, setDownloading] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.eventItem(id),
    enabled: !!id,
    queryFn: async () => {
      const { data: res } = await eventsService.get(id);
      return res;
    },
  });

  const register = useMutation({
    mutationFn: (registered) => eventsService.register(id, registered),
    onSuccess: (res) => {
      queryClient.setQueryData(queryKeys.eventItem(id), res.data);
      queryClient.invalidateQueries({ queryKey: ['events'] });
    },
    onError: (err) => setActionError(extractError(err)),
  });

  const reminder = useMutation({
    mutationFn: (enabled) => eventsService.reminder(id, enabled),
    onSuccess: (res) => {
      queryClient.setQueryData(queryKeys.eventItem(id), res.data);
      queryClient.invalidateQueries({ queryKey: ['events'] });
    },
    onError: (err) => setActionError(extractError(err)),
  });

  if (isLoading) return <Spinner />;
  if (error || !data) return <Alert>{t('common.noResults')}</Alert>;

  const item = localizedEvent(data, i18n.language);
  const when = item.is_all_day ? formatDate(item.starts_at) : formatDateTime(item.starts_at);
  const canRegister = item.status === 'published' && item.allows_registration && item.kind !== 'national_holiday';
  const busy = register.isPending || reminder.isPending;

  const handleDownload = async () => {
    setDownloading(true);
    setActionError('');
    try {
      await downloadIcs(item.id, item.title);
    } catch (err) {
      setActionError(extractError(err));
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="page-shell">
      <Breadcrumb
        items={[
          { to: '/events', label: t('events.title') },
          { label: item.title },
        ]}
      />

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <EventKindBadge kind={item.kind} />
        {item.status === 'cancelled' && (
          <span className="rounded-full bg-rose-100 px-2.5 py-0.5 text-xs font-medium text-rose-800">
            {t('events.status.cancelled')}
          </span>
        )}
        {canEdit && (
          <Link to={`/events/${item.id}/edit`} className="btn-secondary ms-auto text-sm">
            {t('common.edit')}
          </Link>
        )}
      </div>

      <h1 className="mt-4 font-display text-3xl font-semibold text-ink-900 dark:text-slate-100">
        {item.title}
      </h1>
      <div className="mt-3 flex flex-wrap gap-2">
        <ReadAloudButton
          text={`${item.title}. ${when}. ${item.location || ''}. ${item.description || ''}`}
        />
        <WhatsAppShareButton title={item.title} path={`/events/${item.id}`} />
      </div>
      <p className="mt-2 text-sm text-ink-700/70 dark:text-slate-400">
        {when}
        {item.location ? ` · ${item.location}` : ''}
      </p>
      {item.spots_left != null && (
        <p className="mt-1 text-sm text-ink-700/60 dark:text-slate-500">
          {t('events.spotsLeft', { count: item.spots_left })}
        </p>
      )}

      {item.status === 'cancelled' && (
        <div className="mt-6">
          <Alert kind="warning">{t('events.cancelledNotice')}</Alert>
        </div>
      )}
      {actionError && (
        <div className="mt-4">
          <Alert>{actionError}</Alert>
        </div>
      )}

      <div className="mt-6 flex flex-wrap gap-2">
        <a
          href={item.google_calendar_url}
          className="btn-secondary text-sm"
          target="_blank"
          rel="noreferrer"
        >
          {t('events.addGoogle')}
        </a>
        <button type="button" className="btn-secondary text-sm" onClick={handleDownload} disabled={downloading}>
          {downloading ? t('common.loading') : t('events.downloadIcs')}
        </button>
      </div>

      {!user ? (
        <GuestSaveCta className="mt-6" />
      ) : (
        <div className="mt-6 flex flex-wrap gap-2">
          {canRegister && (
            <button
              type="button"
              className={item.user_registered ? 'btn-secondary text-sm' : 'btn-primary text-sm'}
              disabled={busy}
              onClick={() => {
                setActionError('');
                register.mutate(!item.user_registered);
              }}
            >
              {item.user_registered ? t('events.unregister') : t('events.register')}
            </button>
          )}
          {item.status !== 'cancelled' && (
            <button
              type="button"
              className="btn-secondary text-sm"
              disabled={busy}
              onClick={() => {
                setActionError('');
                reminder.mutate(!item.user_reminder);
              }}
            >
              {item.user_reminder ? t('events.clearReminder') : t('events.setReminder')}
            </button>
          )}
        </div>
      )}

      <div
        className="prose mt-8 max-w-none dark:prose-invert"
        dangerouslySetInnerHTML={{ __html: renderMarkdown(item.description) }}
      />

      {item.source_name && (
        <p className="mt-6 text-sm text-ink-700/70 dark:text-slate-400">
          {t('events.source')}:{' '}
          {item.source_url ? (
            <a href={item.source_url} className="font-medium underline" target="_blank" rel="noreferrer">
              {item.source_name}
            </a>
          ) : (
            <span className="font-medium">{item.source_name}</span>
          )}
        </p>
      )}
    </div>
  );
}
