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

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    registerSW({ immediate: false });
  });
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>
);
