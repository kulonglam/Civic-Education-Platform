import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { applyA11ySettings, DEFAULT_A11Y, readA11ySettings, writeA11ySettings } from '../lib/a11y';
import { stopSpeaking } from '../lib/speech';

const AccessibilityContext = createContext(null);

export function AccessibilityProvider({ children }) {
  const [settings, setSettings] = useState(() => {
    if (typeof window === 'undefined') return DEFAULT_A11Y;
    return readA11ySettings();
  });

  useEffect(() => {
    applyA11ySettings(settings);
    writeA11ySettings(settings);
  }, [settings]);

  useEffect(() => () => stopSpeaking(), []);

  const setFontScale = useCallback((fontScale) => {
    setSettings((prev) => ({ ...prev, fontScale }));
  }, []);

  const setHighContrast = useCallback((highContrast) => {
    setSettings((prev) => ({ ...prev, highContrast: Boolean(highContrast) }));
  }, []);

  const value = useMemo(
    () => ({
      fontScale: settings.fontScale,
      highContrast: settings.highContrast,
      setFontScale,
      setHighContrast,
    }),
    [settings.fontScale, settings.highContrast, setFontScale, setHighContrast],
  );

  return <AccessibilityContext.Provider value={value}>{children}</AccessibilityContext.Provider>;
}

export function useAccessibility() {
  const ctx = useContext(AccessibilityContext);
  if (!ctx) {
    throw new Error('useAccessibility must be used within AccessibilityProvider');
  }
  return ctx;
}
