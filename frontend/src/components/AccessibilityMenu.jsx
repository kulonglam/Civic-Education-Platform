import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAccessibility } from '../context/AccessibilityContext';
import { FONT_SCALES, pagePlainText } from '../lib/a11y';
import { isSpeechSupported, speak, stopSpeaking } from '../lib/speech';

export function AccessibilityMenu() {
  const { t, i18n } = useTranslation();
  const { fontScale, highContrast, setFontScale, setHighContrast } = useAccessibility();
  const [open, setOpen] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const ref = useRef(null);
  const supported = isSpeechSupported();

  useEffect(() => {
    if (!open) return undefined;
    const close = (event) => {
      if (ref.current && !ref.current.contains(event.target)) setOpen(false);
    };
    const onKey = (event) => {
      if (event.key === 'Escape') setOpen(false);
    };
    document.addEventListener('mousedown', close);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', close);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  useEffect(() => () => stopSpeaking(), []);

  const togglePageSpeech = () => {
    if (speaking) {
      stopSpeaking();
      setSpeaking(false);
      return;
    }
    const started = speak(pagePlainText(), {
      lang: i18n.language,
      onEnd: () => setSpeaking(false),
      onError: () => setSpeaking(false),
    });
    setSpeaking(Boolean(started));
  };

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        className="icon-btn"
        aria-label={t('a11y.menuLabel')}
        aria-haspopup="dialog"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
      >
        <span className="flex h-4 w-4 items-center justify-center text-sm font-bold leading-none" aria-hidden="true">
          A
        </span>
      </button>
      {open && (
        <div
          role="dialog"
          aria-label={t('a11y.panelTitle')}
          className="absolute right-0 z-40 mt-1.5 w-72 max-w-[calc(100vw-1.5rem)] rounded-xl border border-ink-100 bg-white/95 p-4 shadow-lift backdrop-blur-sm dark:border-slate-700 dark:bg-slate-800"
        >
          <p className="font-display text-sm font-semibold text-ink-900 dark:text-slate-100">
            {t('a11y.panelTitle')}
          </p>
          <p className="mt-1 text-xs text-ink-700/70 dark:text-slate-400">{t('a11y.panelHint')}</p>

          <fieldset className="mt-4">
            <legend className="text-xs font-semibold uppercase tracking-wide text-ink-700 dark:text-slate-300">
              {t('a11y.fontSize')}
            </legend>
            <div className="mt-2 grid grid-cols-4 gap-1">
              {FONT_SCALES.map((scale) => (
                <button
                  key={scale.id}
                  type="button"
                  className={`min-h-11 rounded-lg border px-1 py-2 text-xs font-semibold ${
                    fontScale === scale.id
                      ? 'border-brand-600 bg-brand-50 text-brand-900 dark:border-brand-400 dark:bg-brand-900/40 dark:text-brand-100'
                      : 'border-ink-200 text-ink-800 hover:bg-ink-50 dark:border-slate-600 dark:text-slate-200'
                  }`}
                  aria-pressed={fontScale === scale.id}
                  onClick={() => setFontScale(scale.id)}
                >
                  {scale.percent}%
                </button>
              ))}
            </div>
          </fieldset>

          <label className="mt-4 flex items-center gap-2 text-sm font-medium text-ink-800 dark:text-slate-200">
            <input
              type="checkbox"
              className="h-4 w-4 accent-brand-700"
              checked={highContrast}
              onChange={(event) => setHighContrast(event.target.checked)}
            />
            {t('a11y.highContrast')}
          </label>

          {supported && (
            <button
              type="button"
              className="btn-secondary mt-4 w-full text-sm"
              aria-pressed={speaking}
              onClick={togglePageSpeech}
            >
              {speaking ? t('a11y.stopReading') : t('a11y.readPage')}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
