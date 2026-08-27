import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { MAP_SIZE, projectLonLat, ringsToPath, SOUTH_SUDAN_STATES } from '../lib/southSudanMap';
import type { CivicEvent, MapRegion } from '../types/api';

function fillForCount(count = 0, max = 0) {
  if (!count) return 'var(--map-empty, #e2e8f0)';
  const t = max > 0 ? count / max : 0;
  if (t > 0.66) return '#0f766e';
  if (t > 0.33) return '#14b8a6';
  return '#99f6e4';
}

export function CivicMap({
  regions = [],
  events = [],
}: {
  regions?: MapRegion[];
  events?: CivicEvent[];
}) {
  const { t, i18n } = useTranslation();
  const [selected, setSelected] = useState('');
  const regionByKey = useMemo(
    () => Object.fromEntries(regions.map((row) => [row.key, row])),
    [regions],
  );
  const maxEvents = Math.max(0, ...regions.map((row) => row.upcoming_event_count || 0));
  const selectedEvents = events.filter((event) => (event.region || '') === selected);

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1.4fr)_minmax(16rem,1fr)]">
      <svg
        viewBox={`0 0 ${MAP_SIZE.width} ${MAP_SIZE.height}`}
        role="img"
        aria-label={t('map.aria')}
        className="w-full overflow-visible rounded-2xl border border-ink-100 bg-sky-50 dark:border-slate-700 dark:bg-slate-900"
      >
        {SOUTH_SUDAN_STATES.map((state) => {
          const meta = regionByKey[state.key];
          const count = meta?.upcoming_event_count || 0;
          const active = selected === state.key;
          return (
            <path
              key={state.key}
              d={ringsToPath(state.rings)}
              fill={fillForCount(count, maxEvents)}
              fillRule="evenodd"
              stroke={active ? '#0f172a' : '#64748b'}
              strokeWidth={active ? 2.4 : 1}
              className="cursor-pointer"
              onClick={() => {
                setSelected(state.key);
              }}
            >
              <title>
                {t(`profile.region_${state.key}`)} — {t('map.upcomingCount', { count })}
              </title>
            </path>
          );
        })}
        {events.map((event) => {
          if (event.longitude == null || event.latitude == null) return null;
          const [x, y] = projectLonLat(event.longitude, event.latitude);
          return (
            <circle
              key={event.id}
              cx={x}
              cy={y}
              r={selected && event.region === selected ? 6 : 4.5}
              fill={event.status === 'cancelled' ? '#e11d48' : '#1d4ed8'}
              stroke="#fff"
              strokeWidth="1.5"
            >
              <title>{i18n.language === 'ar' && event.title_ar ? event.title_ar : event.title}</title>
            </circle>
          );
        })}
      </svg>
      <div>
        {selected ? (
          <>
            <h3 className="font-display text-lg font-semibold text-ink-900 dark:text-slate-100">
              {t(`profile.region_${selected}`)}
            </h3>
            <p className="mt-1 text-sm text-ink-700/70 dark:text-slate-400">
              {t('map.upcomingCount', { count: regionByKey[selected]?.upcoming_event_count || 0 })}
              {regionByKey[selected]?.learner_count != null
                ? ` · ${t('map.learners', { count: regionByKey[selected].learner_count })}`
                : ` · ${t('map.learnersHidden')}`}
            </p>
            <ul className="mt-4 space-y-2">
              {selectedEvents.length === 0 ? (
                <li className="text-sm text-ink-700/60 dark:text-slate-400">{t('map.noEvents')}</li>
              ) : (
                selectedEvents.map((event) => (
                  <li key={event.id}>
                    <Link to={`/events/${event.id}`} className="text-sm font-medium text-brand-700 hover:underline dark:text-brand-300">
                      {i18n.language === 'ar' && event.title_ar ? event.title_ar : event.title}
                    </Link>
                  </li>
                ))
              )}
            </ul>
          </>
        ) : (
          <p className="text-sm text-ink-700/70 dark:text-slate-400">{t('map.clickHint')}</p>
        )}
      </div>
    </div>
  );
}
