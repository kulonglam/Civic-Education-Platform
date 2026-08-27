import { useEffect, useState } from 'react';

export function notificationSocketUrl(token) {
  const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';
  const origin = String(apiBase).replace(/\/api(?:\/v1)?\/?$/, '');
  const proto = origin.startsWith('https') ? 'wss' : 'ws';
  const host = origin.replace(/^https?:\/\//, '');
  const query = token ? `?token=${encodeURIComponent(token)}` : '';
  return `${proto}://${host}/ws/notifications/${query}`;
}

export function useNotificationSocket({ enabled, token, onNotification } = {}) {
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!enabled || typeof WebSocket === 'undefined') {
      setConnected(false);
      return undefined;
    }
    let socket;
    let pingId;
    try {
      socket = new WebSocket(notificationSocketUrl(token));
    } catch {
      setConnected(false);
      return undefined;
    }
    socket.onopen = () => {
      setConnected(true);
      pingId = window.setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: 'ping' }));
        }
      }, 25000);
    };
    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload?.type === 'notification') {
          onNotification?.(payload);
        }
      } catch {
        /* ignore malformed frames */
      }
    };
    socket.onerror = () => setConnected(false);
    socket.onclose = () => setConnected(false);
    return () => {
      if (pingId) window.clearInterval(pingId);
      socket.close();
      setConnected(false);
    };
  }, [enabled, token, onNotification]);

  return connected;
}
