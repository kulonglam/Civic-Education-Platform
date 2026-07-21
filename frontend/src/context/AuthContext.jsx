import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { tokenStore, tenantStore } from '../lib/api';
import { authService, userService } from '../lib/services';

const AuthContext = createContext(undefined);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

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
      if (!tokenStore.hasSession) {
        sessionStorage.setItem('cep_session', '1');
      }
    } catch {
      tokenStore.clear();
      setUser(null);
    }
  }, []);

  useEffect(() => {
    (async () => {
      // After reload, memory is empty but httpOnly cookies may still authenticate.
      if (!tokenStore.access && sessionStorage.getItem('cep_session')) {
        try {
          const { data } = await userService.profile();
          setUser(data);
        } catch {
          // Attempt cookie-based refresh then profile again.
          try {
            const { data: tokens } = await authService.refreshSession();
            if (tokens?.access) tokenStore.set(tokens.access, tokens.refresh);
            const { data } = await userService.profile();
            setUser(data);
          } catch {
            tokenStore.clear();
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
      tokenStore.clear();
    };
    window.addEventListener('cep:logout', handler);
    return () => window.removeEventListener('cep:logout', handler);
  }, []);

  // Idle session timeout for privileged roles (complements server-side idle checks).
  useEffect(() => {
    if (!user) return;
    const privileged =
      ['admin', 'editor', 'moderator'].includes(user.role?.name) || Boolean(user.mfa_required);
    if (!privileged) return;

    const IDLE_MS = 30 * 60 * 1000;
    let timer = null;
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
  }, [user]);

  const login = useCallback(
    async (email, password) => {
      const { data } = await authService.login(email, password);
      if (data.mfa_required) {
        return {
          mfaRequired: true,
          mfaToken: data.mfa_token,
        };
      }
      tokenStore.set(data.access, data.refresh);
      await refreshUser();
      return {
        mfaSetupRequired: Boolean(data.mfa_setup_required),
      };
    },
    [refreshUser],
  );

  const verifyMfaLogin = useCallback(
    async (mfaToken, code) => {
      const { data } = await authService.verifyMfaLogin(mfaToken, code);
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
    setUser(null);
  }, []);

  const hasRole = useCallback(
    (...roles) => (user ? roles.includes(user.role.name) : false),
    [user],
  );
  const isPlatformAdmin = useCallback(() => user?.role?.name === 'admin', [user]);

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      verifyMfaLogin,
      logout,
      refreshUser,
      hasRole,
      isPlatformAdmin,
    }),
    [user, loading, login, verifyMfaLogin, logout, refreshUser, hasRole, isPlatformAdmin],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export { AuthProvider, useAuth }; // eslint-disable-line react-refresh/only-export-components -- context + hook pair
