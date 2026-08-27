import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Alert } from './ui';

export function InstallPrompt() {
  const { t } = useTranslation();
  const [prompt, setPrompt] = useState<any>(null);
  const [dismissed, setDismissed] = useState(
    () => sessionStorage.getItem('cep:pwa-dismissed') === '1',
  );

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      setPrompt(e);
    };
    window.addEventListener('beforeinstallprompt', handler);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  if (!prompt || dismissed) return null;

  const install = async () => {
    await prompt.prompt();
    setPrompt(null);
    sessionStorage.setItem('cep:pwa-dismissed', '1');
    setDismissed(true);
  };

  const dismiss = () => {
    sessionStorage.setItem('cep:pwa-dismissed', '1');
    setDismissed(true);
    setPrompt(null);
  };

  return (
    <div className="border-b border-brand-100 bg-brand-50 px-4 py-3 dark:border-brand-900/40 dark:bg-brand-950/30">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3">
        <Alert kind="warning">{t('pwa.installHint')}</Alert>
        <div className="flex gap-2">
          <button type="button" className="btn-primary text-sm" onClick={install}>
            {t('pwa.install')}
          </button>
          <button type="button" className="btn-secondary text-sm" onClick={dismiss}>
            {t('common.cancel')}
          </button>
        </div>
      </div>
    </div>
  );
}
