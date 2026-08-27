import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { Alert, PageHeader, Spinner } from '../components/ui';
import { CivicMap } from '../components/CivicMap';
import { extractError } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { mapService } from '../lib/services';

export function MapPage() {
  const { t } = useTranslation();
  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.civicMap,
    queryFn: async () => {
      const { data: res } = await mapService.civic();
      return res;
    },
  });

  return (
    <div className="page-shell">
      <PageHeader title={t('map.title')} subtitle={t('map.subtitle')} />
      {isLoading && <Spinner />}
      {error && <Alert>{extractError(error)}</Alert>}
      {data && (
        <>
          <CivicMap regions={data.regions} events={data.events} />
          <p className="mt-6 text-xs text-ink-700/55 dark:text-slate-500">{t('map.privacy')}</p>
        </>
      )}
    </div>
  );
}
