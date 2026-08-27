import { useQuery } from '@tanstack/react-query';
import { createContext, useCallback, useContext, useMemo, type ReactNode } from 'react';
import { tokenStore, tenantStore } from '../lib/api';
import { normalizePrimaryColor } from '../lib/theme';
import { queryKeys } from '../lib/queryKeys';
import { organizationService } from '../lib/services';
import { useAuth } from './AuthContext';
import type { OrganizationContextValue } from '../types/cep';
import type { Membership } from '../types/api';
import { unwrapList } from '../types/api';

const OrganizationContext = createContext<OrganizationContextValue | null>(null);

function OrganizationProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();

  const {
    data,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: queryKeys.organization,
    enabled: !!user && !!tokenStore.access,
    queryFn: async () => {
      if (tokenStore.access) {
        tenantStore.syncFromToken(tokenStore.access);
      }
      const [orgRes, membersRes] = await Promise.all([
        organizationService.current(),
        organizationService.members(),
      ]);
      const mine: Membership | null =
        unwrapList(membersRes.data).find((m) => m.user_email === user?.email) ?? null;
      return { organization: orgRes.data, membership: mine };
    },
  });

  const refresh = useCallback(async () => {
    const result = await refetch();
    return result.data;
  }, [refetch]);

  const rawOrganization = data?.organization ?? null;
  const organization = useMemo(
    () =>
      rawOrganization
        ? {
            ...rawOrganization,
            primary_color: normalizePrimaryColor(rawOrganization.primary_color),
          }
        : null,
    [rawOrganization],
  );
  const membership = data?.membership ?? null;
  const isOrgAdmin = membership?.role === 'owner' || membership?.role === 'admin';
  const isOrgContentManager =
    isOrgAdmin || membership?.role === 'content_manager';
  const isOrgModerator =
    isOrgAdmin || membership?.role === 'moderator';

  const value = useMemo(
    () => ({
      organization,
      membership,
      loading: isLoading,
      refresh,
      isOrgAdmin,
      isOrgContentManager,
      isOrgModerator,
    }),
    [organization, membership, isLoading, refresh, isOrgAdmin, isOrgContentManager, isOrgModerator]
  );

  return (
    <OrganizationContext.Provider value={value}>{children}</OrganizationContext.Provider>
  );
}

function useOrganization(): OrganizationContextValue {
  const ctx = useContext(OrganizationContext);
  if (!ctx) throw new Error('useOrganization must be used within OrganizationProvider');
  return ctx;
}

export { OrganizationProvider };
// eslint-disable-next-line react-refresh/only-export-components
export { useOrganization };
