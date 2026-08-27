export function isSpeechSupported(): boolean {
  return typeof window !== 'undefined' && 'speechSynthesis' in window && typeof SpeechSynthesisUtterance === 'function';
}

export function isRecognitionSupported(): boolean {
  return (
    typeof window !== 'undefined' &&
    Boolean(window.SpeechRecognition || window.webkitSpeechRecognition)
  );
}

export function recognitionLanguage(lang = 'en'): string {
  return lang === 'ar' ? 'ar-EG' : 'en-US';
}

type RecognizerHandlers = {
  lang?: string;
  onResult?: (payload: { transcript: string; isFinal: boolean }) => void;
  onError?: (error: unknown) => void;
  onEnd?: () => void;
};

export function createSpeechRecognizer({
  lang = 'en',
  onResult,
  onError,
  onEnd,
}: RecognizerHandlers = {}) {
  if (!isRecognitionSupported()) return null;
  const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Ctor) return null;
  const recognition = new Ctor() as {
    lang: string;
    interimResults: boolean;
    continuous: boolean;
    start: () => void;
    stop: () => void;
    onresult: ((event: { resultIndex: number; results: ArrayLike<{ isFinal: boolean; 0?: { transcript?: string } }> }) => void) | null;
    onerror: ((event: { error?: string }) => void) | null;
    onend: (() => void) | null;
  };
  recognition.lang = recognitionLanguage(lang);
  recognition.interimResults = true;
  recognition.continuous = false;
  recognition.onresult = (event) => {
    let interim = '';
    let finalText = '';
    const results = event.results;
    for (let i = event.resultIndex; i < results.length; i += 1) {
      const transcript = results[i][0]?.transcript || '';
      if (results[i].isFinal) finalText += transcript;
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

export function stopSpeaking(): void {
  if (!isSpeechSupported()) return;
  window.speechSynthesis.cancel();
}

type VoiceLike = { lang?: string; name?: string };

export function pickVoice(lang = 'en', voices: VoiceLike[] = []): VoiceLike | null {
  const prefix = lang === 'ar' ? 'ar' : 'en';
  const preferred = lang === 'ar' ? 'ar-eg' : 'en-us';
  const list = voices || [];
  const normalized = (voice: VoiceLike) => (voice.lang || '').toLowerCase().replace('_', '-');
  return (
    list.find((voice) => normalized(voice) === preferred) ||
    list.find((voice) => normalized(voice).startsWith(`${prefix}-`)) ||
    list.find((voice) => normalized(voice).startsWith(prefix)) ||
    null
  );
}

function getVoicesSafe(): SpeechSynthesisVoice[] {
  if (!isSpeechSupported() || typeof window.speechSynthesis.getVoices !== 'function') {
    return [];
  }
  return window.speechSynthesis.getVoices() || [];
}

function waitForVoices(): Promise<SpeechSynthesisVoice[]> {
  const existing = getVoicesSafe();
  if (existing.length) return Promise.resolve(existing);
  if (!isSpeechSupported() || typeof window.speechSynthesis.addEventListener !== 'function') {
    return Promise.resolve([]);
  }
  return new Promise((resolve) => {
    const finish = () => {
      window.speechSynthesis.removeEventListener('voiceschanged', onChange);
      resolve(getVoicesSafe());
    };
    const onChange = () => finish();
    window.speechSynthesis.addEventListener('voiceschanged', onChange);
    window.setTimeout(finish, 750);
  });
}

type SpeakOptions = {
  lang?: string;
  onEnd?: () => void;
  onError?: (error: unknown) => void;
};

export function speak(text: string, { lang = 'en', onEnd, onError }: SpeakOptions = {}): boolean {
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
  const start = (voices: VoiceLike[]) => {
    const utterance = new SpeechSynthesisUtterance(cleaned);
    utterance.lang = lang === 'ar' ? 'ar-EG' : 'en-US';
    utterance.rate = 0.95;
    const voice = pickVoice(lang, voices);
    if (voice) utterance.voice = voice as SpeechSynthesisVoice;
    utterance.onend = () => onEnd?.();
    utterance.onerror = (event) => onError?.(event.error || event);
    window.speechSynthesis.speak(utterance);
  };
  const voices = getVoicesSafe();
  if (voices.length) {
    start(voices);
  } else {
    void waitForVoices().then(start);
  }
  return true;
}

declare global {
  interface Window {
    SpeechRecognition?: new () => {
      lang: string;
      interimResults: boolean;
      continuous: boolean;
      onresult: ((event: { resultIndex: number; results: ArrayLike<{ isFinal: boolean; 0?: { transcript?: string } }> }) => void) | null;
      onerror: ((event: { error?: string }) => void) | null;
      onend: (() => void) | null;
    };
    webkitSpeechRecognition?: Window['SpeechRecognition'];
  }
}
