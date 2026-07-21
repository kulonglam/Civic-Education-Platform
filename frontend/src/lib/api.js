import axios from 'axios';
import { normalizeLanguage } from '../i18n/languages';
import { getOrgSlugFromToken } from './jwt';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';
const ACCESS_KEY = 'cep_access';
const REFRESH_KEY = 'cep_refresh';
const ORG_SLUG_KEY = 'cep_org_slug';
const SESSION_FLAG = 'cep_session';
const DEFAULT_TENANT_SLUG = import.meta.env.VITE_DEFAULT_TENANT_SLUG || 'platform-demo';

if (!localStorage.getItem(ORG_SLUG_KEY) && DEFAULT_TENANT_SLUG) {
  localStorage.setItem(ORG_SLUG_KEY, DEFAULT_TENANT_SLUG);
}

/** Clear legacy localStorage JWTs (XSS surface). Cookies + memory are authoritative. */
function clearLegacyTokenStorage() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

clearLegacyTokenStorage();

export const tenantStore = {
  get slug() {
    return localStorage.getItem(ORG_SLUG_KEY);
  },
  set(slug) {
    localStorage.setItem(ORG_SLUG_KEY, slug);
  },
  clear() {
    localStorage.removeItem(ORG_SLUG_KEY);
  },
  syncFromToken(access) {
    const slug = getOrgSlugFromToken(access);
    if (slug) tenantStore.set(slug);
  },
};

let memoryAccess = null;
let memoryRefresh = null;

/**
 * In-memory JWT store. Access/refresh are not persisted to localStorage.
 * httpOnly cookies (set by the API) survive reloads; `cep_session` marks an active session.
 */
export const tokenStore = {
  get access() {
    return memoryAccess;
  },
  get refresh() {
    return memoryRefresh;
  },
  get hasSession() {
    return Boolean(memoryAccess || sessionStorage.getItem(SESSION_FLAG));
  },
  set(access, refresh) {
    memoryAccess = access;
    if (refresh) memoryRefresh = refresh;
    sessionStorage.setItem(SESSION_FLAG, '1');
    clearLegacyTokenStorage();
    tenantStore.syncFromToken(access);
  },
  clear() {
    memoryAccess = null;
    memoryRefresh = null;
    sessionStorage.removeItem(SESSION_FLAG);
    clearLegacyTokenStorage();
    tenantStore.clear();
  },
};

export const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = tokenStore.access;
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  const lang = normalizeLanguage(localStorage.getItem('cep_lang'));
  if (config.headers) {
    config.headers['Accept-Language'] = lang;
  }
  const tenantSlug = tenantStore.slug;
  if (tenantSlug && config.headers) {
    config.headers['X-Tenant-Slug'] = tenantSlug;
  }
  return config;
});

let isRefreshing = false;
let pendingQueue = [];

function flushQueue(error, token) {
  pendingQueue.forEach((p) => {
    if (token) p.resolve(token);
    else p.reject(error);
  });
  pendingQueue = [];
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;
    const data = error.response?.data;
    const code =
      data?.code ||
      (typeof data?.detail === 'object' && data.detail ? data.detail.code : null);

    if (status === 401 && (code === 'session_idle' || code === 'session_revoked')) {
      tokenStore.clear();
      window.dispatchEvent(new Event('cep:logout'));
      return Promise.reject(error);
    }

    if (status === 401 && originalRequest && !originalRequest._retry && tokenStore.hasSession) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingQueue.push({
            resolve: (token) => {
              if (token && originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${token}`;
              }
              resolve(api(originalRequest));
            },
            reject,
          });
        });
      }
      originalRequest._retry = true;
      isRefreshing = true;
      try {
        const body = tokenStore.refresh ? { refresh: tokenStore.refresh } : {};
        const { data: refreshData } = await axios.post(
          `${BASE_URL}/auth/token/refresh/`,
          body,
          { withCredentials: true },
        );
        const newAccess = refreshData.access;
        tokenStore.set(newAccess, refreshData.refresh ?? tokenStore.refresh);
        flushQueue(null, newAccess);
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newAccess}`;
        }
        return api(originalRequest);
      } catch (refreshError) {
        flushQueue(refreshError, null);
        tokenStore.clear();
        window.dispatchEvent(new Event('cep:logout'));
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    if (status === 402) {
      const detail = extractError(error);
      window.dispatchEvent(new CustomEvent('cep:quota-exceeded', { detail }));
    }
    return Promise.reject(error);
  },
);

export function extractError(err) {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data;
    if (typeof data === 'string') return data;
    if (data && typeof data === 'object') {
      const detail = data.detail;
      if (typeof detail === 'string') return detail;
      if (detail && typeof detail === 'object' && 'detail' in detail) {
        const nested = detail.detail;
        if (typeof nested === 'string') return nested;
      }
      const firstKey = Object.keys(data)[0];
      if (firstKey) {
        const val = data[firstKey];
        if (Array.isArray(val)) return `${firstKey}: ${val[0]}`;
        return `${firstKey}: ${String(val)}`;
      }
    }
    return err.message;
  }
  return 'An unexpected error occurred.';
}
