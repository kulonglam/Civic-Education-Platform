import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Toaster } from 'react-hot-toast';
import { useQuery } from '@tanstack/react-query';
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import { useDarkMode } from '../hooks/useDarkMode';
import { LanguageSwitcher } from './LanguageSwitcher';
import { OrgSwitcher } from './OrgSwitcher';
import { QuotaBanner } from './QuotaBanner';
import { OfflineBanner } from './OfflineBanner';
import { EmailVerifyBanner } from './EmailVerifyBanner';
import { InstallPrompt } from './InstallPrompt';
import { PushNotificationPrompt } from './PushNotificationPrompt';
import { ArrowUp, Moon, Sun } from './Icons';
import { notificationService } from '../lib/services';
import { queryKeys } from '../lib/queryKeys';
import { PlatformLogo } from './PlatformLogo';

function navLinkClass({ isActive }) {
  return `rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
    isActive
      ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300'
      : 'text-gray-600 hover:bg-gray-100 dark:text-slate-300 dark:hover:bg-slate-800'
  }`;
}

function NavDropdown({ label, avatar, badge, items, align = 'left' }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    const close = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', close);
    return () => document.removeEventListener('mousedown', close);
  }, [open]);

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') setOpen(false);
  };

  if (items.length === 0) return null;

  return (
    <div ref={ref} className="relative" onKeyDown={handleKeyDown}>
      <button
        type="button"
        className={`relative flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
          open
            ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300'
            : 'text-gray-600 hover:bg-gray-100 dark:text-slate-300 dark:hover:bg-slate-800'
        }`}
        aria-expanded={open}
        aria-haspopup="menu"
        onClick={() => setOpen((v) => !v)}
      >
        {avatar && (
          <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold text-white">
            {avatar}
          </span>
        )}
        {label}
        {badge > 0 && (
          <span className="absolute -right-0.5 -top-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
            {badge > 9 ? '9+' : badge}
          </span>
        )}
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M6 9l6 6 6-6" />
        </svg>
      </button>

      {open && (
        <div
          role="menu"
          className={`absolute top-full z-30 mt-1 min-w-[11rem] rounded-xl border border-gray-200 bg-white py-1 shadow-lg dark:border-slate-700 dark:bg-slate-800 ${
            align === 'right' ? 'right-0' : 'left-0'
          }`}
        >
          {items.map((item, idx) => {
            if (item.divider) {
              return <hr key={`d-${idx}`} className="my-1 border-gray-100 dark:border-slate-700" />;
            }
            if (item.onClick) {
              return (
                <button
                  key={item.label}
                  type="button"
                  role="menuitem"
                  className="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 dark:text-slate-300 dark:hover:bg-slate-700"
                  onClick={() => { setOpen(false); item.onClick(); }}
                >
                  {item.label}
                </button>
              );
            }
            return (
              <NavLink
                key={item.to}
                to={item.to}
                role="menuitem"
                className={({ isActive }) =>
                  `flex items-center justify-between px-4 py-2 text-sm ${
                    isActive
                      ? 'bg-brand-50 font-medium text-brand-700 dark:bg-brand-900/30 dark:text-brand-300'
                      : 'text-gray-700 hover:bg-gray-50 dark:text-slate-300 dark:hover:bg-slate-700'
                  }`
                }
                onClick={() => setOpen(false)}
              >
                {item.label}
                {item.badge > 0 && (
                  <span className="ml-2 flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
                    {item.badge > 99 ? '99+' : item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </div>
      )}
    </div>
  );
}

function MobileSection({ title, children }) {
  if (!children) return null;
  return (
    <div className="pt-2">
      {title && (
        <p className="px-3 pb-1 text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-slate-500">
          {title}
        </p>
      )}
      <div className="flex flex-col gap-1">{children}</div>
    </div>
  );
}

export function Layout() {
  const { t } = useTranslation();
  const { user, logout, hasRole, isPlatformAdmin } = useAuth();
  const { organization, isOrgAdmin } = useOrganization();
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [showTop, setShowTop] = useState(false);
  const [routeLoading, setRouteLoading] = useState(false);
  const [dark, setDark] = useDarkMode();

  // Brief loading flash on every route change
  useEffect(() => {
    setRouteLoading(true);
    const t = setTimeout(() => setRouteLoading(false), 350);
    return () => clearTimeout(t);
  }, [location.pathname]);

  // Back-to-top visibility
  useEffect(() => {
    const onScroll = () => setShowTop(window.scrollY > 400);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Close mobile menu on navigation
  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Unread notifications count (only when logged in, refreshed every 3 min)
  const { data: unreadCount = 0 } = useQuery({
    queryKey: queryKeys.notificationsUnread,
    queryFn: async () => {
      const { data } = await notificationService.list({ page: '1' });
      return (data.results ?? []).filter((n) => !n.is_read).length;
    },
    enabled: !!user,
    staleTime: 3 * 60 * 1000,
    refetchInterval: 3 * 60 * 1000,
  });

  const learnLinks = [
    { to: '/articles', label: t('nav.articles') },
    { to: '/quizzes', label: t('nav.quizzes'), auth: true },
    { to: '/forum', label: t('nav.forum') },
    { to: '/tutor', label: t('nav.tutor'), auth: true },
  ].filter((link) => !link.auth || user);

  const manageItems = [];
  if (hasRole('admin', 'editor')) {
    manageItems.push({ to: '/articles/manage', label: t('nav.manageArticles') });
    manageItems.push({ to: '/quizzes/manage', label: t('nav.manageQuizzes') });
  }
  if (hasRole('admin', 'moderator')) {
    manageItems.push({
      to: '/admin',
      label: isPlatformAdmin() ? t('nav.platformAdmin') : t('nav.moderation'),
    });
  }

  const orgItems = isOrgAdmin
    ? [
        { to: '/dashboard', label: t('nav.dashboard') },
        { to: '/organization', label: t('nav.organization') },
        { to: '/billing', label: t('nav.billing') },
      ]
    : [];

  const accountItems = user
    ? [
        { to: '/profile', label: t('nav.profile') },
        { to: '/notifications', label: t('nav.notifications'), badge: unreadCount },
        { divider: true },
        { label: t('nav.logout'), onClick: handleLogout },
      ]
    : [];

  return (
    <div className="flex min-h-screen flex-col">
      {/* Skip to content – accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-brand-600 focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-white focus:shadow-lg"
      >
        Skip to content
      </a>

      {/* Route loading bar */}
      {routeLoading && <div className="route-loading-bar" />}

      <OfflineBanner />
      <EmailVerifyBanner />
      <InstallPrompt />
      <PushNotificationPrompt />
      <QuotaBanner />

      <header className="sticky top-0 z-20 border-b border-gray-200 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-900/90">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3">
          <Link to="/" className="flex min-w-0 shrink items-center gap-2">
            {organization?.logo_url ? (
              <img
                src={organization.logo_url}
                alt={organization.name}
                className="h-9 w-9 shrink-0 rounded-lg object-cover"
              />
            ) : (
              <PlatformLogo className="h-9 w-9" alt={organization?.name ?? t('app.name')} />
            )}
            <span className="truncate text-base font-bold text-gray-900 dark:text-slate-100 lg:text-lg">
              {organization?.name ?? t('app.name')}
            </span>
          </Link>

          <nav className="hidden items-center gap-0.5 lg:flex">
            {learnLinks.map((link) => (
              <NavLink key={link.to} to={link.to} className={navLinkClass}>
                {link.label}
              </NavLink>
            ))}
            <NavDropdown label={t('nav.manage')} items={manageItems} />
            <NavDropdown label={t('nav.organization')} items={orgItems} />
          </nav>

          <div className="flex shrink-0 items-center gap-2">
            {user && <OrgSwitcher />}
            <LanguageSwitcher />

            {/* Dark mode toggle */}
            <button
              type="button"
              aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
              className="rounded-lg border border-gray-300 p-2 text-gray-600 hover:bg-gray-100 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800"
              onClick={() => setDark((d) => !d)}
            >
              {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>

            {user ? (
              <NavDropdown
                label={user.first_name}
                avatar={user.first_name?.charAt(0).toUpperCase()}
                badge={unreadCount}
                items={accountItems}
                align="right"
              />
            ) : (
              <div className="hidden items-center gap-2 lg:flex">
                <Link to="/login" className="btn-secondary text-sm">
                  {t('nav.login')}
                </Link>
                <Link to="/register" className="btn-primary text-sm">
                  {t('nav.register')}
                </Link>
              </div>
            )}

            <button
              type="button"
              className="rounded-lg border border-gray-300 p-2 dark:border-slate-600 dark:text-slate-300 lg:hidden"
              onClick={() => setMenuOpen((v) => !v)}
              aria-label="Menu"
              aria-expanded={menuOpen}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                {menuOpen ? (
                  <path d="M18 6L6 18M6 6l12 12" />
                ) : (
                  <path d="M3 6h18M3 12h18M3 18h18" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {menuOpen && (
          <div className="border-t border-gray-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-900 lg:hidden">
            <div className="flex flex-col gap-1">
              <MobileSection title={t('nav.learn')}>
                {learnLinks.map((link) => (
                  <NavLink key={link.to} to={link.to} className={navLinkClass}>
                    {link.label}
                  </NavLink>
                ))}
              </MobileSection>

              {manageItems.length > 0 && (
                <MobileSection title={t('nav.manage')}>
                  {manageItems.map((item) => (
                    <NavLink key={item.to} to={item.to} className={navLinkClass}>
                      {item.label}
                    </NavLink>
                  ))}
                </MobileSection>
              )}

              {orgItems.length > 0 && (
                <MobileSection title={t('nav.organization')}>
                  {orgItems.map((item) => (
                    <NavLink key={item.to} to={item.to} className={navLinkClass}>
                      {item.label}
                    </NavLink>
                  ))}
                </MobileSection>
              )}

              {user && (
                <MobileSection title={t('nav.myAccount')}>
                  {accountItems.map((item, idx) => {
                    if (item.divider) return <hr key={`d-${idx}`} className="my-1 border-gray-100 dark:border-slate-700" />;
                    if (item.onClick) {
                      return (
                        <button
                          key={item.label}
                          type="button"
                          className="rounded-lg px-3 py-2 text-left text-sm font-medium text-gray-600 hover:bg-gray-100 dark:text-slate-300 dark:hover:bg-slate-800"
                          onClick={() => { setMenuOpen(false); item.onClick(); }}
                        >
                          {item.label}
                        </button>
                      );
                    }
                    return (
                      <NavLink key={item.to} to={item.to} className={navLinkClass}>
                        <span className="flex items-center justify-between">
                          {item.label}
                          {item.badge > 0 && (
                            <span className="flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
                              {item.badge > 99 ? '99+' : item.badge}
                            </span>
                          )}
                        </span>
                      </NavLink>
                    );
                  })}
                </MobileSection>
              )}

              {!user && (
                <div className="mt-3 flex gap-2 border-t border-gray-100 pt-3 dark:border-slate-700">
                  <Link to="/login" className="btn-secondary w-full">
                    {t('nav.login')}
                  </Link>
                  <Link to="/register" className="btn-primary w-full">
                    {t('nav.register')}
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </header>

      <main id="main-content" className="mx-auto w-full max-w-6xl flex-1 px-4 py-8">
        <div key={location.pathname} className="page-enter">
          <Outlet />
        </div>
      </main>

      <footer className="border-t border-gray-200 bg-white py-8 dark:border-slate-800 dark:bg-slate-900">
        <div className="mx-auto max-w-6xl px-4">
          <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
            <p className="text-sm text-gray-500 dark:text-slate-400">
              © {new Date().getFullYear()} {t('app.name')}. {t('app.tagline')}.
            </p>
            <nav className="flex gap-5 text-sm text-gray-400 dark:text-slate-500">
              <Link to="/privacy" className="transition-colors hover:text-gray-600 dark:hover:text-slate-300">{t('footer.privacy')}</Link>
              <Link to="/terms" className="transition-colors hover:text-gray-600 dark:hover:text-slate-300">{t('footer.terms')}</Link>
              <a href="mailto:support@civiced.org" className="transition-colors hover:text-gray-600 dark:hover:text-slate-300">{t('footer.contact')}</a>
            </nav>
          </div>
        </div>
      </footer>

      {/* Back to top */}
      {showTop && (
        <button
          type="button"
          aria-label="Back to top"
          className="fixed bottom-6 right-6 z-40 flex h-10 w-10 items-center justify-center rounded-full bg-brand-600 text-white shadow-lg transition-all hover:bg-brand-700 hover:shadow-xl"
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        >
          <ArrowUp className="h-5 w-5" />
        </button>
      )}

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3500,
          style: { fontSize: '0.875rem', maxWidth: '360px' },
          success: { iconTheme: { primary: '#047857', secondary: '#fff' } },
          error:   { iconTheme: { primary: '#dc2626', secondary: '#fff' } },
        }}
      />
    </div>
  );
}
