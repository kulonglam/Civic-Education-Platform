import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { tenantStore } from '../lib/api';
import { queryKeys } from '../lib/queryKeys';
import { organizationService } from '../lib/services';
import { useOrganization } from '../context/OrganizationContext';

export function OrgSwitcher() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { organization, refresh } = useOrganization();

  const { data: memberships = [] } = useQuery({
    queryKey: queryKeys.myOrganizations,
    queryFn: async () => {
      const { data } = await organizationService.mine();
      return data;
    },
  });

  const switchOrg = useMutation({
    mutationFn: async (slug) => {
      tenantStore.set(slug);
      await refresh();
    },
    onSuccess: () => {
      queryClient.invalidateQueries();
    },
  });

  if (memberships.length <= 1) return null;

  const currentSlug = organization?.slug ?? tenantStore.slug ?? '';

  return (
    <label className="hidden items-center gap-2 md:flex">
      <span className="sr-only">{t('saas.switchOrg')}</span>
      <select
        className="input max-w-[180px] py-1.5 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        value={currentSlug}
        disabled={switchOrg.isPending}
        onChange={(e) => switchOrg.mutate(e.target.value)}
        aria-label={t('saas.switchOrg')}
      >
        {memberships.map((m) => (
          <option key={m.id} value={m.organization.slug}>
            {m.organization.name}
          </option>
        ))}
      </select>
    </label>
  );
}
