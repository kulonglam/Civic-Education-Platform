import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

export function MfaSetupCard({
  enabled,
  required,
  setup,
  code,
  busy,
  onStart,
  onCodeChange,
  onConfirm,
}) {
  const { t } = useTranslation();
  const [qrUrl, setQrUrl] = useState('');

  useEffect(() => {
    const uri = setup?.provisioning_uri;
    if (!uri) {
      setQrUrl('');
      return undefined;
    }
    let cancelled = false;
    import('qrcode')
      .then((mod) => {
        const QRCode = mod.default || mod;
        return QRCode.toDataURL(uri, { width: 220, margin: 1, errorCorrectionLevel: 'M' });
      })
      .then((url) => {
        if (!cancelled) setQrUrl(url);
      })
      .catch(() => {
        if (!cancelled) setQrUrl('');
      });
    return () => {
      cancelled = true;
    };
  }, [setup?.provisioning_uri]);

  if (!required && !enabled) return null;

  return (
    <div className="card mt-6 space-y-4">
      <h2 className="text-sm font-semibold text-ink-900 dark:text-slate-100">{t('profile.mfaTitle')}</h2>
      {enabled ? (
        <p className="text-sm text-green-700 dark:text-green-400">{t('profile.mfaEnabled')}</p>
      ) : (
        <>
          <p className="text-sm text-amber-800 dark:text-amber-200">{t('profile.mfaRequiredHint')}</p>
          {!setup ? (
            <button type="button" className="btn-secondary text-sm" onClick={onStart} disabled={!!busy}>
              {busy === 'setup' ? t('common.loading') : t('profile.mfaStartSetup')}
            </button>
          ) : (
            <form onSubmit={onConfirm} className="space-y-3">
              <p className="text-sm text-ink-700 dark:text-slate-300">{t('profile.mfaQrHint')}</p>
              {qrUrl ? (
                <img
                  src={qrUrl}
                  alt={t('profile.mfaQrAlt')}
                  className="h-52 w-52 rounded-xl border border-ink-100 bg-white p-2 dark:border-slate-600"
                />
              ) : (
                <p className="text-xs text-ink-700/70 dark:text-slate-400">{t('profile.mfaQrUnavailable')}</p>
              )}
              <div>
                <label className="label">{t('profile.mfaSecretLabel')}</label>
                <code className="block break-all rounded bg-ink-100 px-2 py-1 text-xs dark:bg-slate-900">
                  {setup.secret}
                </code>
              </div>
              <div>
                <label className="label">{t('profile.mfaConfirmCode')}</label>
                <input
                  className="input"
                  inputMode="numeric"
                  maxLength={6}
                  value={code}
                  onChange={(e) => onCodeChange(e.target.value)}
                  required
                />
              </div>
              <button type="submit" className="btn-primary text-sm" disabled={!!busy || code.trim().length < 6}>
                {busy === 'confirm' ? t('common.loading') : t('profile.mfaConfirm')}
              </button>
            </form>
          )}
        </>
      )}
    </div>
  );
}
