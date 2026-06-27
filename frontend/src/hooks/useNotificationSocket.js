import { useEffect, useRef, useCallback } from 'react';
import { tokenStore } from '../lib/api';

const WS_BASE = import.meta.env.VITE_WS_BASE_URL ?? 'ws://127.0.0.1:8000';

/**
 * Opens a WebSocket to /ws/notifications/ and calls `onNotification` for
 * each incoming notification pushed from the server.
 *
 * Authenticates using the stored access token as a query parameter.
 * Auto-reconnects on unexpected close (max 5 attempts, exponential back-off).
 *
 * @param {(notification: object) => void} onNotification
 * @param {boolean} [enabled=true] set to false to skip connecting (e.g. unauthenticated)
 */
export function useNotificationSocket(onNotification, enabled = true) {
  const wsRef = useRef(null);
  const attemptsRef = useRef(0);
  const timerRef = useRef(null);
  const onNotificationRef = useRef(onNotification);
  onNotificationRef.current = onNotification;

  const connect = useCallback(() => {
    const token = tokenStore.access;
    if (!token || !enabled) return;

    const url = `${WS_BASE}/ws/notifications/?token=${encodeURIComponent(token)}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data);
        if (data.type === 'notification') {
          onNotificationRef.current?.(data);
        }
      } catch {
        // malformed frame — ignore
      }
    };

    ws.onopen = () => {
      attemptsRef.current = 0;
      // Keep-alive ping every 30 s
      timerRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30_000);
    };

    ws.onclose = (evt) => {
      clearInterval(timerRef.current);
      // 4001 = auth failure — don't retry
      if (evt.code === 4001) return;
      if (attemptsRef.current >= 5) return;
      const delay = Math.min(1000 * 2 ** attemptsRef.current, 30_000);
      attemptsRef.current += 1;
      setTimeout(connect, delay);
    };

    ws.onerror = () => ws.close();
  }, [enabled]);

  useEffect(() => {
    if (!enabled) return;
    connect();
    return () => {
      clearInterval(timerRef.current);
      wsRef.current?.close(1000);
    };
  }, [connect, enabled]);
}
