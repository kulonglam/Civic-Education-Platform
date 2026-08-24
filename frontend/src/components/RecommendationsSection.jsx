import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { queryKeys } from '../lib/queryKeys';
import { recommendationService } from '../lib/services';

export function RecommendationsSection({ className = '' }) {
  const { t, i18n } = useTranslation();
  const { data, isError } = useQuery({
    queryKey: queryKeys.recommendations,
    queryFn: async () => {
      const { data: res } = await recommendationService.list();
      return res;
    },
  });

  if (isError || !data?.items?.length) return null;

  return (
    <section className={className}>
      <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="font-display text-xl font-semibold text-ink-900 dark:text-slate-100">
          {t('recommendations.title')}
        </h2>
        {data.personalized ? (
          <p className="text-xs text-ink-700/60 dark:text-slate-400">{t('recommendations.personalized')}</p>
        ) : (
          <p className="text-xs text-ink-700/60 dark:text-slate-400">{t('recommendations.popular')}</p>
        )}
      </div>
      <ul className="grid gap-3 sm:grid-cols-2">
        {data.items.slice(0, 8).map((item) => {
          const title = i18n.language === 'ar' && item.title_ar ? item.title_ar : item.title;
          return (
            <li key={`${item.kind}-${item.id}`}>
              <Link
                to={item.href}
                className="block rounded-xl border border-ink-100 bg-white/80 px-4 py-3 transition-colors hover:border-brand-200 dark:border-slate-700 dark:bg-slate-900/50"
              >
                <p className="font-medium text-ink-900 dark:text-slate-100">{title}</p>
                <p className="mt-1 text-xs text-ink-700/60 dark:text-slate-400">
                  {t(`recommendations.reasons.${item.reason}`, {
                    defaultValue: item.reason,
                    course: item.course_title,
                  })}
                </p>
              </Link>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
