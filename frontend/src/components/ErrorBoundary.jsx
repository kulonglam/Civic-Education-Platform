import { Component } from 'react';
import { useTranslation } from 'react-i18next';

function ErrorFallback({ onRetry }) {
  const { t } = useTranslation();
  return (
    <div className="mx-auto max-w-lg py-16 text-center">
      <h1 className="text-2xl font-bold text-gray-900">{t('errors.boundaryTitle')}</h1>
      <p className="mt-2 text-gray-600">{t('errors.boundaryMessage')}</p>
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
    console.error('UI error:', error, info.componentStack);
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
