import { PLATFORM_LOGO_ALT, PLATFORM_LOGO_URL } from '../lib/branding';

export function PlatformLogo({ className = 'h-10 w-10', alt = PLATFORM_LOGO_ALT }) {
  return (
    <img
      src={PLATFORM_LOGO_URL}
      alt={alt}
      className={`shrink-0 object-contain ${className}`}
    />
  );
}
