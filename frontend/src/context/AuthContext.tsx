import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { tokenStore, tenantStore } from '../lib/api';
import { authService, organizationService, userService } from '../lib/services';
import i18n from '../i18n';
import { normalizeLanguage } from '../i18n/languages';
import { isPlatformAdminRole, isSuperAdminRole, platformRoleAllowed } from '../lib/roles';
import type { AuthContextValue, Impersonation, PlatformUser } from '../types/cep';

const AuthContext = createContext<AuthContextValue | null>(null);

function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<PlatformUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [impersonation, setImpersonation] = useState<Impersonation>(null);

  useEffect(() => {
    if (tokenStore.access) {
      tenantStore.syncFromToken(tokenStore.access);
    }
  }, []);

  const refreshUser = useCallback(async () => {
    // Cookie session or in-memory JWT — try profile; API auth uses cookies when Bearer missing.
    if (!tokenStore.hasSession && !tokenStore.access) {
      setUser(null);
      return;
    }
    try {
      const { data } = await userService.profile();
      setUser(data);
      if (data?.impersonator_email) {
        setImpersonation({
          actorEmail: data.impersonator_email,
          targetEmail: data.email,
          targetName: `${data.first_name || ''} ${data.last_name || ''}`.trim(),
        });
      } else {
        setImpersonation(null);
      }
      if (!tokenStore.hasSession) {
        sessionStorage.setItem('cep_session', '1');
      }
    } catch {
      tokenStore.clear();
      setImpersonation(null);
      setUser(null);
    }
  }, []);

  useEffect(() => {
    (async () => {
      if (!tokenStore.access && sessionStorage.getItem('cep_session')) {
        try {
          await refreshUser();
        } catch {
          try {
            const { data: tokens } = await authService.refreshSession();
            if (tokens?.access) tokenStore.set(tokens.access, tokens.refresh);
            await refreshUser();
          } catch {
            tokenStore.clear();
            setImpersonation(null);
            setUser(null);
          }
        }
      } else {
        await refreshUser();
      }
      setLoading(false);
    })();
  }, [refreshUser]);

  useEffect(() => {
    const handler = () => {
      setUser(null);
      setImpersonation(null);
      tokenStore.clear();
    };
    window.addEventListener('cep:logout', handler);
    return () => window.removeEventListener('cep:logout', handler);
  }, []);

  useEffect(() => {
    const preferred = user?.profile?.preferred_language;
    if (!preferred) return;
    const lang = normalizeLanguage(preferred);
    if (normalizeLanguage(i18n.language) !== lang) {
      i18n.changeLanguage(lang);
    }
  }, [user?.id, user?.profile?.preferred_language]);

  // Idle session timeout for privileged roles (complements server-side idle checks).
  useEffect(() => {
    if (!user || impersonation) return;
    const privileged =
      ['admin', 'editor', 'moderator'].includes(user.role?.name || '') || Boolean(user.mfa_required);
    if (!privileged) return;

    const IDLE_MS = 30 * 60 * 1000;
    let timer: number | null = null;
    const bump = () => {
      if (timer) window.clearTimeout(timer);
      timer = window.setTimeout(() => {
        window.dispatchEvent(new Event('cep:logout'));
      }, IDLE_MS);
    };
    const events = ['mousemove', 'keydown', 'click', 'touchstart', 'scroll'];
    events.forEach((evt) => window.addEventListener(evt, bump, { passive: true }));
    bump();
    return () => {
      if (timer) window.clearTimeout(timer);
      events.forEach((evt) => window.removeEventListener(evt, bump));
    };
  }, [user, impersonation]);

  const login = useCallback(
    async (email: string, password: string) => {
      const { data } = await authService.login(email, password);
      if (data.mfa_required) {
        return {
          mfaRequired: true,
          mfaToken: data.mfa_token,
        };
      }
      if (!data.access) throw new Error('Login failed');
      tokenStore.set(data.access, data.refresh);
      await refreshUser();
      return {
        mfaSetupRequired: Boolean(data.mfa_setup_required),
      };
    },
    [refreshUser],
  );

  const verifyMfaLogin = useCallback(
    async (mfaToken: string, code: string) => {
      const { data } = await authService.verifyMfaLogin(mfaToken, code);
      if (!data.access) throw new Error('MFA verification failed');
      tokenStore.set(data.access, data.refresh);
      await refreshUser();
    },
    [refreshUser],
  );

  const logout = useCallback(async () => {
    const refresh = tokenStore.refresh;
    try {
      await authService.logout(refresh || undefined);
    } catch {
      /* ignore logout errors */
    }
    tokenStore.clear();
    setImpersonation(null);
    setUser(null);
  }, []);

  const startImpersonation = useCallback(
    async (orgId: string | number, userId: string | number) => {
      const { data } = await organizationService.impersonate(String(orgId), String(userId));
      if (!data.access) throw new Error('Impersonation failed');
      tokenStore.set(data.access, data.refresh);
      setImpersonation({
        actorEmail: data.actor?.email,
        targetEmail: data.target?.email,
        targetName: data.target?.full_name,
      });
      await refreshUser();
      return data;
    },
    [refreshUser],
  );

  const exitImpersonation = useCallback(async () => {
    const { data } = await organizationService.exitImpersonation();
    if (!data.access) throw new Error('Exit impersonation failed');
    tokenStore.set(data.access, data.refresh);
    setImpersonation(null);
    await refreshUser();
    return data;
  }, [refreshUser]);

  const hasRole = useCallback(
    (...roles: string[]) => (user ? platformRoleAllowed(user.role?.name, roles) : false),
    [user],
  );
  const isPlatformAdmin = useCallback(() => isPlatformAdminRole(user?.role?.name), [user]);
  const isSuperAdmin = useCallback(() => isSuperAdminRole(user?.role?.name), [user]);

  const value = useMemo(
    () => ({
      user,
      loading,
      impersonation,
      login,
      verifyMfaLogin,
      logout,
      refreshUser,
      startImpersonation,
      exitImpersonation,
      hasRole,
      isPlatformAdmin,
      isSuperAdmin,
    }),
    [
      user,
      loading,
      impersonation,
      login,
      verifyMfaLogin,
      logout,
      refreshUser,
      startImpersonation,
      exitImpersonation,
      hasRole,
      isPlatformAdmin,
      isSuperAdmin,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export { AuthProvider, useAuth }; // eslint-disable-line react-refresh/only-export-components -- context + hook pair
