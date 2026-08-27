// @ts-nocheck
import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link, useSearchParams } from 'react-router-dom';
import { EVENT_KINDS, EventKindBadge } from '../components/EventKindBadge';
import { ChevronLeft, ChevronRight } from '../components/Icons';
import { Pagination } from '../components/Pagination';
import { Alert, CardSkeleton, EmptyState, PageHeader } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import { formatDate, formatDateTime } from '../lib/format';
import { localizedEvent } from '../lib/localizedContent';
import { queryKeys } from '../lib/queryKeys';
import { eventsService } from '../lib/services';

const PAGE_SIZE = 20;

function monthBounds(year, month) {
  const start = new Date(year, month, 1);
  const end = new Date(year, month + 1, 1);
  return { start: start.toISOString(), end: end.toISOString() };
}

function buildMonthCells(year, month) {
  const first = new Date(year, month, 1);
  const startOffset = first.getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const cells = [];
  for (let i = 0; i < startOffset; i += 1) cells.push(null);
  for (let day = 1; day <= daysInMonth; day += 1) cells.push(new Date(year, month, day));
  while (cells.length % 7 !== 0) cells.push(null);
  return cells;
}

function isSameDay(iso, date) {
  const value = new Date(iso);
  return (
    value.getFullYear() === date.getFullYear() &&
    value.getMonth() === date.getMonth() &&
    value.getDate() === date.getDate()
  );
}

export function EventsPage() {
  const { t, i18n } = useTranslation();
  const { hasRole } = useAuth();
  const { isOrgContentManager } = useOrganization();
  const canManage = hasRole('admin', 'editor') || isOrgContentManager;
  const [searchParams, setSearchParams] = useSearchParams();
  const [page, setPage] = useState(1);
  const now = new Date();
  const [cursor, setCursor] = useState({ year: now.getFullYear(), month: now.getMonth() });

  const kind = searchParams.get('kind') || '';
  const bounds = monthBounds(cursor.year, cursor.month);
  const weekdayLabels = [0, 1, 2, 3, 4, 5, 6].map((offset) => {
    const date = new Date(2026, 7, 23 + offset);
    return date.toLocaleDateString(i18n.language === 'ar' ? 'ar-EG' : 'en-US', { weekday: 'short' });
  });

  const calendarParams = useMemo(() => {
    const params = {
      page_size: '100',
      starts_after: bounds.start,
      starts_before: bounds.end,
    };
    if (kind) params.kind = kind;
    return params;
  }, [bounds.start, bounds.end, kind]);

  const upcomingParams = useMemo(() => {
    const params = {
      page: String(page),
      starts_after: new Date().toISOString(),
    };
    if (kind) params.kind = kind;
    return params;
  }, [page, kind]);

  const { data: calendarData, isLoading: calendarLoading, isError: calendarError } = useQuery({
    queryKey: queryKeys.events(calendarParams),
    queryFn: async () => {
      const { data: res } = await eventsService.list(calendarParams);
      return res;
    },
  });

  const { data: upcomingData, isLoading: upcomingLoading, isError: upcomingError } = useQuery({
    queryKey: queryKeys.events(upcomingParams),
    queryFn: async () => {
      const { data: res } = await eventsService.list(upcomingParams);
      return res;
    },
  });

  const calendarItems = (calendarData?.results ?? []).map((item) => localizedEvent(item, i18n.language));
  const upcomingItems = (upcomingData?.results ?? []).map((item) => localizedEvent(item, i18n.language));
  const totalCount = upcomingData?.count ?? 0;
  const cells = buildMonthCells(cursor.year, cursor.month);
  const monthLabel = new Date(cursor.year, cursor.month, 1).toLocaleDateString(
    i18n.language === 'ar' ? 'ar-EG' : 'en-US',
    { month: 'long', year: 'numeric' },
  );

  const setFilter = (value) => {
    const next = new URLSearchParams(searchParams);
    if (value) next.set('kind', value);
    else next.delete('kind');
    setSearchParams(next, { replace: true });
    setPage(1);
  };

  const shiftMonth = (delta) => {
    setCursor((prev) => {
      const next = new Date(prev.year, prev.month + delta, 1);
      return { year: next.getFullYear(), month: next.getMonth() };
    });
  };

  return (
    <div className="page-shell">
      <PageHeader
        eyebrow={t('nav.learn')}
        title={t('events.title')}
        subtitle={t('events.subtitle')}
      />

      {canManage && (
        <div className="mb-6 flex justify-end">
          <Link to="/events/manage" className="btn-secondary text-sm">
            {t('events.manage')}
          </Link>
        </div>
      )}

      <div className="filter-bar mb-6 flex flex-col gap-3 sm:flex-row sm:items-center">
        <select
          className="input sm:max-w-xs"
          value={kind}
          aria-label={t('events.filterKind')}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="">{t('events.allKinds')}</option>
          {EVENT_KINDS.map((value) => (
            <option key={value} value={value}>
              {t(`events.kinds.${value}`)}
            </option>
          ))}
        </select>
      </div>

      {(calendarError || upcomingError) && <Alert>{t('common.noResults')}</Alert>}

      <section className="card mb-8 p-4 sm:p-5" aria-labelledby="events-calendar-title">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 id="events-calendar-title" className="font-display text-lg font-semibold text-ink-900 dark:text-slate-100">
            {monthLabel}
          </h2>
          <div className="flex gap-2">
            <button type="button" className="btn-secondary p-2" onClick={() => shiftMonth(-1)} aria-label={t('events.prevMonth')}>
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button type="button" className="btn-secondary p-2" onClick={() => shiftMonth(1)} aria-label={t('events.nextMonth')}>
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
        {calendarLoading ? (
          <CardSkeleton />
        ) : (
          <div className="grid grid-cols-7 gap-1 text-sm">
            {weekdayLabels.map((label) => (
              <div key={label} className="px-1 pb-2 text-center text-xs font-medium text-ink-700/60 dark:text-slate-500">
                {label}
              </div>
            ))}
            {cells.map((date, index) => {
              if (!date) {
                return <div key={`empty-${index}`} className="min-h-20 rounded-lg bg-ink-50/50 dark:bg-slate-900/40" />;
              }
              const dayEvents = calendarItems.filter((item) => isSameDay(item.starts_at, date));
              const isToday = isSameDay(now.toISOString(), date);
              return (
                <div
                  key={date.toISOString()}
                  className={`min-h-20 rounded-lg border p-1.5 ${
                    isToday
                      ? 'border-brand-400 bg-brand-50/80 dark:border-brand-700 dark:bg-brand-950/30'
                      : 'border-ink-100 bg-white dark:border-slate-800 dark:bg-slate-900'
                  }`}
                >
                  <p className="text-xs font-medium text-ink-700 dark:text-slate-300">{date.getDate()}</p>
                  <div className="mt-1 grid gap-1">
                    {dayEvents.slice(0, 2).map((item) => (
                      <Link
                        key={item.id}
                        to={`/events/${item.id}`}
                        className="block truncate rounded bg-brand-100 px-1 py-0.5 text-[11px] text-brand-900 hover:bg-brand-200 dark:bg-brand-950/70 dark:text-brand-100"
                      >
                        {item.title}
                      </Link>
                    ))}
                    {dayEvents.length > 2 && (
                      <p className="text-[11px] text-ink-700/60 dark:text-slate-500">
                        {t('events.moreOnDay', { count: dayEvents.length - 2 })}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      <h2 className="mb-4 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">
        {t('events.upcoming')}
      </h2>
      {upcomingLoading && <CardSkeleton />}
      {!upcomingLoading && upcomingItems.length === 0 && <EmptyState title={t('events.empty')} />}
      <div className="grid gap-4">
        {upcomingItems.map((item) => (
          <Link
            key={item.id}
            to={`/events/${item.id}`}
            className="card block p-5 transition hover:-translate-y-0.5 hover:shadow-lift"
          >
            <div className="flex flex-wrap items-center gap-2">
              <EventKindBadge kind={item.kind} />
              {item.status === 'cancelled' && (
                <span className="rounded-full bg-rose-100 px-2.5 py-0.5 text-xs font-medium text-rose-800">
                  {t('events.status.cancelled')}
                </span>
              )}
            </div>
            <h3 className="mt-3 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">
              {item.title}
            </h3>
            <p className="mt-2 text-sm text-ink-700/75 dark:text-slate-400">
              {item.is_all_day ? formatDate(item.starts_at) : formatDateTime(item.starts_at)}
              {item.location ? ` · ${item.location}` : ''}
            </p>
          </Link>
        ))}
      </div>
      {totalCount > PAGE_SIZE && (
        <Pagination page={page} pageSize={PAGE_SIZE} totalCount={totalCount} onPageChange={setPage} />
      )}
    </div>
  );
}
