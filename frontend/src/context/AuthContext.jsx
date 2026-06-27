import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { tokenStore, tenantStore } from "../lib/api";
import { authService, userService } from "../lib/services";
const AuthContext = createContext(void 0);
function AuthProvider({
  children
}) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    if (tokenStore.access) {
      tenantStore.syncFromToken(tokenStore.access);
    }
  }, []);
  const refreshUser = useCallback(async () => {
    if (!tokenStore.access) {
      setUser(null);
      return;
    }
    try {
      const {
        data
      } = await userService.profile();
      setUser(data);
    } catch {
      setUser(null);
    }
  }, []);
  useEffect(() => {
    (async () => {
      await refreshUser();
      setLoading(false);
    })();
  }, [refreshUser]);
  useEffect(() => {
    const handler = () => {
      setUser(null);
      tokenStore.clear();
    };
    window.addEventListener("cep:logout", handler);
    return () => window.removeEventListener("cep:logout", handler);
  }, []);
  const login = useCallback(async (email, password) => {
    const {
      data
    } = await authService.login(email, password);
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
  }, [refreshUser]);
  const verifyMfaLogin = useCallback(async (mfaToken, code) => {
    const {
      data
    } = await authService.verifyMfaLogin(mfaToken, code);
    tokenStore.set(data.access, data.refresh);
    await refreshUser();
  }, [refreshUser]);
  const logout = useCallback(async () => {
    const refresh = tokenStore.refresh;
    if (refresh) {
      try {
        await authService.logout(refresh);
      } catch {
        /* ignore logout errors */
      }
    }
    tokenStore.clear();
    setUser(null);
  }, []);
  const hasRole = useCallback((...roles) => user ? roles.includes(user.role.name) : false, [user]);
  const isPlatformAdmin = useCallback(() => user?.role?.name === 'admin', [user]);
  const value = useMemo(() => ({
    user,
    loading,
    login,
    verifyMfaLogin,
    logout,
    refreshUser,
    hasRole,
    isPlatformAdmin
  }), [user, loading, login, verifyMfaLogin, logout, refreshUser, hasRole, isPlatformAdmin]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export { AuthProvider };
// eslint-disable-next-line react-refresh/only-export-components
export { useAuth };
