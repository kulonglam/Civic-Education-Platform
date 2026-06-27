import { StrictMode, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClientProvider } from '@tanstack/react-query';
import { registerSW } from 'virtual:pwa-register';
import { queryClient } from './lib/queryClient';
import { initSentry } from './lib/sentry';
import { startOfflineSync } from './lib/offline/sync';
import './i18n';
import './index.css';
import App from './App';

initSentry();

if ('serviceWorker' in navigator) {
  registerSW({ immediate: true });
}

function Root() {
  useEffect(() => startOfflineSync(), []);

  return (
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  );
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Root />
  </StrictMode>
);
