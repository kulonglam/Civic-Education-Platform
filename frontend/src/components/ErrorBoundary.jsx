import { Component } from 'react';
import { useTranslation } from 'react-i18next';
import { captureUiError } from '../lib/sentry';

function ErrorFallback({ onRetry }) {
  const { t } = useTranslation();
  return (
    <div className="mx-auto max-w-lg py-16 text-center" role="alert">
      <h1 className="font-display text-2xl font-semibold text-ink-900 dark:text-slate-100">
        {t('errors.boundaryTitle')}
      </h1>
      <p className="mt-2 text-ink-700/70 dark:text-slate-400">{t('errors.boundaryMessage')}</p>
      <button type="button" className="btn-primary mt-6" onClick={onRetry}>
        {t('errors.tryAgain')}
      </button>
    </div>
  );
}

class ErrorBoundary extends Component {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    captureUiError(error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <ErrorFallback onRetry={() => this.setState({ hasError: false })} />
      );
    }
    return this.props.children;
  }
}

export { ErrorBoundary };
