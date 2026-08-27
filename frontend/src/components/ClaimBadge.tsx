import { useTranslation } from 'react-i18next';

export const NEWS_TOPICS = [
  'announcement',
  'education_update',
  'election',
  'law_policy',
  'awareness',
];

export const NEWS_CLAIM_TYPES = [
  'verified_fact',
  'educational',
  'opinion',
  'unverified',
];

const CLAIM_STYLES = {
  verified_fact:
    'border-emerald-300 bg-emerald-50 text-emerald-900 dark:border-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-200',
  educational:
    'border-brand-200 bg-brand-50 text-brand-800 dark:border-brand-800 dark:bg-brand-950/40 dark:text-brand-200',
  opinion:
    'border-amber-300 bg-amber-50 text-amber-900 dark:border-amber-800 dark:bg-amber-950/50 dark:text-amber-200',
  unverified:
    'border-red-300 bg-red-50 text-red-800 dark:border-red-900 dark:bg-red-950/50 dark:text-red-200',
};

const CLAIM_ALERT = {
  verified_fact: 'success',
  educational: 'info',
  opinion: 'warning',
  unverified: 'error',
} as const;

type ClaimType = keyof typeof CLAIM_STYLES;

export function claimAlertKind(claimType?: string): 'error' | 'success' | 'info' | 'warning' {
  return CLAIM_ALERT[(claimType as ClaimType) || 'educational'] || 'info';
}

export function ClaimBadge({ claimType, className = '' }: { claimType?: string; className?: string }) {
  const { t } = useTranslation();
  if (!claimType) return null;
  const styles = CLAIM_STYLES[(claimType as ClaimType) || 'educational'] || CLAIM_STYLES.educational;
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${styles} ${className}`}
    >
      {t(`news.claims.${claimType}`)}
    </span>
  );
}

export function TopicBadge({ topic, className = '' }: { topic?: string; className?: string }) {
  const { t } = useTranslation();
  if (!topic) return null;
  return (
    <span
      className={`inline-flex items-center rounded-full border border-ink-200 bg-white px-2.5 py-0.5 text-xs font-medium text-ink-700 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 ${className}`}
    >
      {t(`news.topics.${topic}`)}
    </span>
  );
}

export function ClaimLegend({ className = '' }) {
  const { t } = useTranslation();
  return (
    <section
      className={`rounded-2xl border border-ink-100 bg-white/80 p-4 shadow-soft dark:border-slate-800 dark:bg-slate-900/60 ${className}`}
      aria-labelledby="news-claim-legend"
    >
      <h2 id="news-claim-legend" className="text-sm font-semibold text-ink-900 dark:text-slate-100">
        {t('news.legendTitle')}
      </h2>
      <p className="mt-1 text-sm text-ink-700/75 dark:text-slate-400">{t('news.legendIntro')}</p>
      <ul className="mt-4 grid gap-3 sm:grid-cols-2">
        {NEWS_CLAIM_TYPES.map((claimType) => (
          <li key={claimType} className="flex flex-col gap-1">
            <ClaimBadge claimType={claimType} />
            <p className="text-xs leading-relaxed text-ink-700/70 dark:text-slate-400">
              {t(`news.legend.${claimType}`)}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
