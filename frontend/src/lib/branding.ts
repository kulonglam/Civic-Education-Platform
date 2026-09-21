/** Platform logo served from /public (Civic Education brand mark). */
export const PLATFORM_LOGO_URL = '/civic-education-logo.png';

export const PLATFORM_NAME = 'CivicHub';
export const PLATFORM_SHORT_NAME = 'CivicHub';

export const PLATFORM_LOGO_ALT = PLATFORM_NAME;

const LEGACY_PLATFORM_NAMES = new Set([
  'Civic Education RSS',
  'Civic RSS',
  'التعليم المدني RSS',
]);

/** Map stored org/source names that still use the former product title. */
export function displayOrganizationName(
  name: string | null | undefined,
  productName: string = PLATFORM_NAME,
): string {
  if (!name || LEGACY_PLATFORM_NAMES.has(name)) return productName;
  return name;
}
