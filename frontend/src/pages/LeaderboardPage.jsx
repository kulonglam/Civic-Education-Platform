import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Alert, PageHeader, Spinner } from '../components/ui';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { gamificationService } from '../lib/services';

export function LeaderboardPage() {
  const { t } = useTranslation();
  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.leaderboard,
    queryFn: async () => {
      const { data: res } = await gamificationService.leaderboard();
      return res;
    },
  });

  return (
    <div className="page-shell mx-auto max-w-3xl">
      <PageHeader title={t('leaderboard.title')} subtitle={t('leaderboard.subtitle')} />
      {isLoading && <Spinner />}
      {error && <Alert>{extractError(error)}</Alert>}
      {data?.me && (
        <p className="mb-4 rounded-xl border border-brand-200 bg-brand-50 px-4 py-3 text-sm dark:border-brand-800 dark:bg-brand-950/40">
          {t('leaderboard.yourRank', { rank: data.me.rank, xp: data.me.xp_points })}
        </p>
      )}
      {data && (
        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>{t('leaderboard.rank')}</th>
                <th>{t('leaderboard.learner')}</th>
                <th>{t('leaderboard.level')}</th>
                <th>{t('leaderboard.xp')}</th>
                <th>{t('leaderboard.badges')}</th>
              </tr>
            </thead>
            <tbody>
              {(data.entries || []).map((row) => (
                <tr key={row.user_id} className={row.is_me ? 'bg-brand-50/70 dark:bg-brand-950/30' : ''}>
                  <td>{row.rank}</td>
                  <td>{row.is_me ? t('leaderboard.you', { name: row.display_name }) : row.display_name}</td>
                  <td>{row.level}</td>
                  <td>{row.xp_points}</td>
                  <td>{row.badges_earned}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
