import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { createSpeechRecognizer, isRecognitionSupported } from '../lib/speech';

export function VoiceInputButton({ onTranscript, className = '', disabled = false }) {
  const { t, i18n } = useTranslation();
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);
  const supported = isRecognitionSupported();

  useEffect(() => () => {
    recognitionRef.current?.stop?.();
  }, []);

  if (!supported) return null;

  const toggle = () => {
    if (listening) {
      recognitionRef.current?.stop?.();
      setListening(false);
      return;
    }
    const recognition = createSpeechRecognizer({
      lang: i18n.language,
      onResult: ({ transcript, isFinal }) => {
        if (isFinal && transcript) onTranscript?.(transcript);
      },
      onError: () => setListening(false),
      onEnd: () => setListening(false),
    });
    if (!recognition) return;
    recognitionRef.current = recognition;
    try {
      recognition.start();
      setListening(true);
    } catch {
      setListening(false);
    }
  };

  return (
    <button
      type="button"
      className={`btn-secondary text-sm ${className}`}
      onClick={toggle}
      disabled={disabled}
      aria-pressed={listening}
      aria-label={listening ? t('voice.stop') : t('voice.start')}
    >
      {listening ? t('voice.stop') : t('voice.start')}
    </button>
  );
}
