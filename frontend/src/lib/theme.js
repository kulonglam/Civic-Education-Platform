/** Default organization / app primary brand color (emerald-600). */
export const DEFAULT_PRIMARY_COLOR = '#059669';

/** Legacy Tailwind blue values stored before the green rebrand. */
const LEGACY_BLUE_PRIMARY_COLORS = new Set([
  '#2563eb',
  '#3b82f6',
  '#1d4ed8',
  '#1e40af',
  '#1e3a8a',
  '#60a5fa',
  '#93c5fd',
  '#bfdbfe',
  '#dbeafe',
  '#eff6ff',
]);

/** Map legacy blue org colors to the current green default. */
export function normalizePrimaryColor(color) {
  if (!color) return DEFAULT_PRIMARY_COLOR;
  const normalized = String(color).trim().toLowerCase();
  if (LEGACY_BLUE_PRIMARY_COLORS.has(normalized)) return DEFAULT_PRIMARY_COLOR;
  return color;
}
