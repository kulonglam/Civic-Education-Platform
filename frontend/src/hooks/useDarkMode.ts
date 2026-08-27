import { useEffect, useState } from 'react';

const LIGHT_THEME = '#047857';
const DARK_THEME = '#0f120e';

function syncThemeColor(dark: boolean) {
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute('content', dark ? DARK_THEME : LIGHT_THEME);
  document.documentElement.style.colorScheme = dark ? 'dark' : 'light';
}

export function useDarkMode() {
  const [dark, setDark] = useState(() => {
    const stored = localStorage.getItem('theme');
    if (stored) return stored === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (dark) {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
    syncThemeColor(dark);
  }, [dark]);

  return [dark, setDark] as const;
}
