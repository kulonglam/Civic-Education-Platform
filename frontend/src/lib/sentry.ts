import * as Sentry from '@sentry/react';

export function initSentry() {
  const dsn = import.meta.env.VITE_SENTRY_DSN;
  if (!dsn) return;

  Sentry.init({
    dsn,
    environment: import.meta.env.VITE_SENTRY_ENVIRONMENT || import.meta.env.MODE || 'production',
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],
    tracesSampleRate: Number(import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE || 0.1),
    replaysSessionSampleRate: Number(import.meta.env.VITE_SENTRY_REPLAYS_SESSION || 0),
    replaysOnErrorSampleRate: Number(import.meta.env.VITE_SENTRY_REPLAYS_ON_ERROR || 1),
    sendDefaultPii: false,
  });
}

export function captureUiError(error: unknown, info?: { componentStack?: string | null }) {
  if (!import.meta.env.VITE_SENTRY_DSN) {
    console.error('UI error:', error, info?.componentStack);
    return;
  }
  Sentry.withScope((scope) => {
    if (info?.componentStack) {
      scope.setExtra('componentStack', info.componentStack);
    }
    Sentry.captureException(error);
  });
}

export { Sentry };
