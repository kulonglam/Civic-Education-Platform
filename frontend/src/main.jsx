import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClientProvider } from '@tanstack/react-query';
import { registerSW } from 'virtual:pwa-register';
import { queryClient } from './lib/queryClient';
import { initSentry } from './lib/sentry';
import './i18n';
import './index.css';
import App from './App';

initSentry();

const apiBase = import.meta.env.VITE_API_BASE_URL;
if (apiBase) {
  try {
    const origin = new URL(apiBase, window.location.origin).origin;
    if (origin && origin !== window.location.origin) {
      const link = document.createElement('link');
      link.rel = 'preconnect';
      link.href = origin;
      link.crossOrigin = 'anonymous';
      document.head.appendChild(link);
    }
  } catch {
    /* ignore malformed VITE_API_BASE_URL */
  }
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    registerSW({ immediate: false });
  });
}

const root = document.getElementById('root');
if (root) {
  createRoot(root).render(
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </StrictMode>
  );
}
