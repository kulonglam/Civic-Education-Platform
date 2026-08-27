import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { applyA11ySettings, DEFAULT_A11Y, readA11ySettings, writeA11ySettings, type A11ySettings, type FontScaleId } from '../lib/a11y';
import { stopSpeaking } from '../lib/speech';

type AccessibilityContextValue = {
  fontScale: FontScaleId;
  highContrast: boolean;
  setFontScale: (fontScale: FontScaleId) => void;
  setHighContrast: (highContrast: boolean) => void;
};

const AccessibilityContext = createContext<AccessibilityContextValue | null>(null);

export function AccessibilityProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<A11ySettings>(() => {
    if (typeof window === 'undefined') return DEFAULT_A11Y;
    return readA11ySettings();
  });

  useEffect(() => {
    applyA11ySettings(settings);
    writeA11ySettings(settings);
  }, [settings]);

  useEffect(() => () => stopSpeaking(), []);

  const setFontScale = useCallback((fontScale: FontScaleId) => {
    setSettings((prev) => ({ ...prev, fontScale }));
  }, []);

  const setHighContrast = useCallback((highContrast: boolean) => {
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

export function useAccessibility(): AccessibilityContextValue {
  const ctx = useContext(AccessibilityContext);
  if (!ctx) {
    throw new Error('useAccessibility must be used within AccessibilityProvider');
  }
  return ctx;
}
