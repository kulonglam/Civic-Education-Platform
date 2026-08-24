export function isSpeechSupported() {
  return typeof window !== 'undefined' && 'speechSynthesis' in window && typeof SpeechSynthesisUtterance === 'function';
}

export function isRecognitionSupported() {
  return (
    typeof window !== 'undefined' &&
    Boolean(window.SpeechRecognition || window.webkitSpeechRecognition)
  );
}

export function recognitionLanguage(lang = 'en') {
  return lang === 'ar' ? 'ar-EG' : 'en-US';
}

export function createSpeechRecognizer({
  lang = 'en',
  onResult,
  onError,
  onEnd,
} = {}) {
  if (!isRecognitionSupported()) return null;
  const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new Ctor();
  recognition.lang = recognitionLanguage(lang);
  recognition.interimResults = true;
  recognition.continuous = false;
  recognition.onresult = (event) => {
    let interim = '';
    let finalText = '';
    for (let i = event.resultIndex; i < event.results.length; i += 1) {
      const transcript = event.results[i][0]?.transcript || '';
      if (event.results[i].isFinal) finalText += transcript;
      else interim += transcript;
    }
    onResult?.({
      transcript: (finalText || interim).trim(),
      isFinal: Boolean(finalText.trim()),
    });
  };
  recognition.onerror = (event) => onError?.(event.error || event);
  recognition.onend = () => onEnd?.();
  return recognition;
}

export function stopSpeaking() {
  if (!isSpeechSupported()) return;
  window.speechSynthesis.cancel();
}

export function pickVoice(lang = 'en', voices = []) {
  const prefix = lang === 'ar' ? 'ar' : 'en';
  const preferred = lang === 'ar' ? 'ar-eg' : 'en-us';
  const list = voices || [];
  const normalized = (voice) => (voice.lang || '').toLowerCase().replace('_', '-');
  return (
    list.find((voice) => normalized(voice) === preferred) ||
    list.find((voice) => normalized(voice).startsWith(`${prefix}-`)) ||
    list.find((voice) => normalized(voice).startsWith(prefix)) ||
    null
  );
}

function waitForVoices() {
  if (!isSpeechSupported()) return Promise.resolve([]);
  const existing = window.speechSynthesis.getVoices() || [];
  if (existing.length) return Promise.resolve(existing);
  return new Promise((resolve) => {
    const finish = () => {
      window.speechSynthesis.removeEventListener('voiceschanged', onChange);
      resolve(window.speechSynthesis.getVoices() || []);
    };
    const onChange = () => finish();
    window.speechSynthesis.addEventListener('voiceschanged', onChange);
    window.setTimeout(finish, 750);
  });
}

export function speak(text, { lang = 'en', onEnd, onError } = {}) {
  if (!isSpeechSupported()) {
    onError?.(new Error('Speech synthesis is not available.'));
    return false;
  }
  const cleaned = (text || '').replace(/\s+/g, ' ').trim();
  if (!cleaned) {
    onError?.(new Error('Nothing to read.'));
    return false;
  }
  stopSpeaking();
  const start = (voices) => {
    const utterance = new SpeechSynthesisUtterance(cleaned);
    utterance.lang = lang === 'ar' ? 'ar-EG' : 'en-US';
    utterance.rate = 0.95;
    const voice = pickVoice(lang, voices);
    if (voice) utterance.voice = voice;
    utterance.onend = () => onEnd?.();
    utterance.onerror = (event) => onError?.(event.error || event);
    window.speechSynthesis.speak(utterance);
  };
  const voices = window.speechSynthesis.getVoices() || [];
  if (voices.length) {
    start(voices);
  } else {
    waitForVoices().then(start);
  }
  return true;
}
