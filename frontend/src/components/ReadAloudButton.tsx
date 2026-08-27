import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { isSpeechSupported, speak, stopSpeaking } from '../lib/speech';

export function ReadAloudButton({ text = '', className = '' }) {
  const { t, i18n } = useTranslation();
  const [speaking, setSpeaking] = useState(false);
  const supported = isSpeechSupported();

  useEffect(() => () => stopSpeaking(), []);

  if (!supported) return null;

  const toggle = () => {
    if (speaking) {
      stopSpeaking();
      setSpeaking(false);
      return;
    }
    const started = speak(text, {
      lang: i18n.language,
      onEnd: () => setSpeaking(false),
      onError: () => setSpeaking(false),
    });
    setSpeaking(Boolean(started));
  };

  return (
    <button
      type="button"
      className={`btn-secondary text-sm ${className}`}
      onClick={toggle}
      aria-pressed={speaking}
    >
      {speaking ? t('a11y.stopReading') : t('a11y.readAloud')}
    </button>
  );
}
