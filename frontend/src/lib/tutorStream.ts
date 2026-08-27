import { normalizeLanguage } from '../i18n/languages';
import { tenantStore, tokenStore } from './api';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';

/**
 * Stream tutor chat tokens via SSE. Calls onToken, onDone, onError.
 */
export async function streamTutorChat(
  message: string,
  {
    articleId,
    onToken,
    onDone,
    onError,
    signal,
  }: {
    articleId?: string | number;
    onToken?: (token: string) => void;
    onDone?: (payload?: any) => void;
    onError?: (error: any) => void;
    signal?: AbortSignal;
  } = {},
) {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'text/event-stream',
    'Accept-Language': normalizeLanguage(localStorage.getItem('cep_lang')),
  };
  const token = tokenStore.access;
  if (token) headers.Authorization = `Bearer ${token}`;
  const tenantSlug = tenantStore.slug;
  if (tenantSlug) headers['X-Tenant-Slug'] = tenantSlug;

  let response: Response | undefined;
  try {
    response = await fetch(`${BASE_URL}/tutor/chat/stream/`, {
      method: 'POST',
      headers,
      credentials: 'include',
      body: JSON.stringify({
        message,
        ...(articleId ? { article_id: articleId } : {}),
      }),
      signal,
    });
  } catch (err) {
    onError?.(err);
    return;
  }

  if (!response.ok) {
    let detail = 'Stream request failed.';
    try {
      const data = await response.json();
      detail = data.detail || detail;
    } catch {
      /* ignore */
    }
    onError?.(new Error(detail));
    return;
  }

  const reader = response.body?.getReader();
  if (!reader) {
    onError?.(new Error('Streaming not supported.'));
    return;
  }

  const decoder = new TextDecoder();
  let buffer = '';
  let currentEvent = 'message';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const blocks = buffer.split('\n\n');
    buffer = blocks.pop() || '';

    for (const block of blocks) {
      if (!block.trim()) continue;
      let eventName = currentEvent;
      let dataLine = '';
      for (const line of block.split('\n')) {
        if (line.startsWith('event:')) eventName = line.slice(6).trim();
        if (line.startsWith('data:')) dataLine += line.slice(5).trim();
      }
      if (!dataLine) continue;
      let payload;
      try {
        payload = JSON.parse(dataLine);
      } catch {
        continue;
      }
      if (eventName === 'token' && payload.text) {
        onToken?.(payload.text);
      } else if (eventName === 'done') {
        onDone?.(payload);
      } else if (eventName === 'error') {
        onError?.(new Error(payload.detail || 'Tutor error'));
      }
    }
  }
}
