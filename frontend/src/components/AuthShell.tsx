import { useTranslation } from 'react-i18next';
import type { ReactNode } from 'react';
import { BookOpen, AcademicCap, ShieldCheck } from './Icons';
import { PlatformLogo } from './PlatformLogo';

const FEATURES = [
  { Icon: BookOpen, key: 'home.featureLearnTitle', desc: 'home.featureLearnText' },
  { Icon: AcademicCap, key: 'home.featureQuizTitle', desc: 'home.featureQuizText' },
  { Icon: ShieldCheck, key: 'home.featureForumTitle', desc: 'home.featureForumText' },
];

/**
 * Institutional split-panel shell for auth surfaces (login / register).
 */
export function AuthShell({
  children,
  title,
  subtitle,
  showBrand = true,
}: {
  children: ReactNode;
  title: string;
  subtitle?: string;
  showBrand?: boolean;
}) {
  const { t } = useTranslation();

  return (
    <div className="auth-shell">
      <aside className="auth-brand-panel px-10 py-12 xl:px-14" aria-label={showBrand ? t('app.name') : undefined}>
        <div className="auth-brand-photo" aria-hidden="true" />
        <div
          className="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/55 via-black/15 to-black/25"
          aria-hidden="true"
        />
        <div className="relative flex h-full flex-col justify-between">
          <div>
            {showBrand && (
              <div className="flex items-center gap-3">
                <PlatformLogo className="h-12 w-12 ring-1 ring-white/20" />
                <div>
                  <p className="font-display text-xl font-semibold">{t('app.name')}</p>
                  <p className="mt-0.5 text-sm font-normal text-brand-100/90">{t('app.tagline')}</p>
                </div>
              </div>
            )}
            <p className={`eyebrow text-brand-200 ${showBrand ? 'mt-14' : ''}`}>
              {t('auth.enterpriseEyebrow')}
            </p>
            <h1 className="mt-3 max-w-md font-display text-hero text-white">
              {title}
            </h1>
            {subtitle && (
              <p className="mt-4 max-w-md text-hero-sub text-brand-100/90">{subtitle}</p>
            )}
          </div>
          <ul className="relative mt-12 space-y-4 border-t border-white/15 pt-8">
            {FEATURES.map(({ Icon, key, desc }) => (
              <li key={key} className="flex gap-3">
                <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-white/10 text-brand-200 ring-1 ring-white/10">
                  <Icon className="h-4 w-4" />
                </span>
                <div>
                  <p className="text-sm font-semibold text-white">{t(key)}</p>
                  <p className="mt-0.5 text-sm leading-snug text-brand-100/75">{t(desc)}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </aside>
      <div className="auth-form-panel">
        <div className="w-full max-w-md animate-fade-in">{children}</div>
      </div>
    </div>
  );
}
