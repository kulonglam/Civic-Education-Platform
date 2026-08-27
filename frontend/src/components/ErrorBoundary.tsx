import { Component, type ErrorInfo, type ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { captureUiError } from '../lib/sentry';

function ErrorFallback() {
  const { t } = useTranslation();
  return (
    <div className="mx-auto max-w-lg px-4 py-16 text-center" role="alert">
      <div className="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300">
        <svg className="h-7 w-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" aria-hidden="true">
          <circle cx="12" cy="12" r="9" />
          <path d="M12 8v5M12 16h.01" strokeLinecap="round" />
        </svg>
      </div>
      <h1 className="font-display text-2xl font-semibold text-ink-900 dark:text-slate-100">
        {t('errors.boundaryTitle')}
      </h1>
      <p className="mt-2 text-sm leading-relaxed text-ink-700/70 dark:text-slate-400">{t('errors.boundaryMessage')}</p>
      <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
        <a
          href="/"
          className="btn-primary"
          onClick={(event) => {
            event.preventDefault();
            window.location.assign('/');
          }}
        >
          {t('errors.goHome')}
        </a>
        <button type="button" className="btn-secondary" onClick={() => window.location.reload()}>
          {t('errors.tryAgain')}
        </button>
      </div>
    </div>
  );
}

class ErrorBoundary extends Component<{ children?: ReactNode; resetKey?: string }, { hasError: boolean }> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    captureUiError(error, info);
  }

  componentDidUpdate(prevProps: { children?: ReactNode; resetKey?: string }) {
    if (this.state.hasError && prevProps.resetKey !== this.props.resetKey) {
      this.setState({ hasError: false });
    }
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }
    return this.props.children;
  }
}

export { ErrorBoundary };
