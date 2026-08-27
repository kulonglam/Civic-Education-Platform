import { useTranslation } from 'react-i18next';

export const EVENT_KINDS = [
  'election',
  'public_consultation',
  'community_meeting',
  'workshop',
  'national_holiday',
  'public_hearing',
];

const KIND_CLASS = {
  election: 'bg-violet-100 text-violet-800 dark:bg-violet-950/60 dark:text-violet-200',
  public_consultation: 'bg-sky-100 text-sky-800 dark:bg-sky-950/60 dark:text-sky-200',
  community_meeting: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-200',
  workshop: 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-200',
  national_holiday: 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-200',
  public_hearing: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-200',
};

type EventKind = keyof typeof KIND_CLASS;

export function EventKindBadge({ kind, className = '' }: { kind?: string; className?: string }) {
  const { t } = useTranslation();
  if (!kind) return null;
  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${KIND_CLASS[kind as EventKind] || 'bg-ink-100 text-ink-700'} ${className}`}
    >
      {t(`events.kinds.${kind}`)}
    </span>
  );
}
