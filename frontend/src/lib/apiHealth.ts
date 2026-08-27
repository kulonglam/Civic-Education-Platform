import { api } from './api';

export const API_SLOW_MS = 3500;
export const API_WAKE_EVENT = 'cep:api-waking';
export const API_READY_EVENT = 'cep:api-ready';

export function notifyApiWaking() {
  if (typeof window === 'undefined') return;
  window.dispatchEvent(new Event(API_WAKE_EVENT));
}

export function notifyApiReady() {
  if (typeof window === 'undefined') return;
  window.dispatchEvent(new Event(API_READY_EVENT));
}

export function isWakeFailure(error: unknown) {
  if (!error || typeof error !== 'object') return true;
  const response = 'response' in error ? (error as { response?: { status?: number } }).response : undefined;
  if (!response) return true;
  const status = response.status;
  return status === 502 || status === 504;
}

export async function pingApiReady({ timeout = 20000 }: { timeout?: number } = {}) {
  const { status } = await api.get('/ready/', { timeout, validateStatus: () => true });
  if (status >= 200 && status < 500) return true;
  throw new Error(`ready ${status}`);
}

export function beginApiWarmup() {
  pingApiReady({ timeout: 90000 })
    .then(() => notifyApiReady())
    .catch(() => notifyApiWaking());
}
