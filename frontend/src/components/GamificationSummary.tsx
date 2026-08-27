import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { StatTile } from './ui';
import { queryKeys } from '../lib/queryKeys';
import { gamificationService } from '../lib/services';

export function GamificationSummary({ className = '' }) {
  const { t } = useTranslation();
  const { data: gamification, isLoading } = useQuery({
    queryKey: queryKeys.gamificationMe,
    queryFn: async () => {
      const { data: res } = await gamificationService.me();
      return res;
    },
  });

  if (isLoading) return null;
  if (!gamification) return null;

  return (
    <section className={className}>
      <h2 className="mb-4 font-display text-xl font-semibold text-ink-900 dark:text-slate-100">
        {t('gamification.title')}
      </h2>
      <div className="grid gap-4 sm:grid-cols-3">
        <StatTile label={t('gamification.level')} value={gamification.level} />
        <StatTile label={t('gamification.xp')} value={gamification.xp_points} />
        <StatTile label={t('gamification.nextLevel')} value={gamification.xp_to_next_level} />
      </div>
      {gamification.badges_earned && gamification.badges_earned.length > 0 && (
        <ul className="mt-4 flex flex-wrap gap-2">
          {gamification.badges_earned.map((badge) => (
            <li
              key={badge.slug}
              className="rounded-full border border-brand-200 bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-800 dark:border-brand-800 dark:bg-brand-900/30 dark:text-brand-200"
              title={badge.description}
            >
              {badge.name}
            </li>
          ))}
        </ul>
      )}
      <p className="mt-4 text-sm">
        <Link to="/leaderboard" className="font-semibold text-brand-700 hover:underline dark:text-brand-300">
          {t('gamification.leaderboardLink')}
        </Link>
        {' · '}
        <Link to="/engage" className="font-semibold text-brand-700 hover:underline dark:text-brand-300">
          {t('gamification.engageLink')}
        </Link>
      </p>
    </section>
  );
}
