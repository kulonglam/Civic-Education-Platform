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
  return `nav-link ${isActive ? 'nav-link-active' : 'nav-link-idle'}`;
}

function HeaderSearch() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [query, setQuery] = useState('');

  return (
    <form
      className="hidden min-w-[10rem] max-w-xs flex-1 xl:block"
      onSubmit={(e) => {
        e.preventDefault();
        const q = query.trim();
        if (q.length < 2) return;
        navigate(`/search?q=${encodeURIComponent(q)}`);
      }}
    >
      <label className="sr-only" htmlFor="header-search">
        {t('search.placeholder')}
      </label>
      <input
        id="header-search"
        type="search"
        className="input py-2 text-sm"
        placeholder={t('search.placeholder')}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
    </form>
  );
}

function HeaderSearchLink() {
  const { t } = useTranslation();
  return (
    <Link
      to="/search"
      className="hidden rounded-xl border border-ink-200 p-2 text-ink-700 hover:bg-ink-100/70 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800 lg:inline-flex xl:hidden"
      aria-label={t('nav.search')}
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <circle cx="11" cy="11" r="8" />
        <path d="M21 21l-4.35-4.35" />
      </svg>
    </Link>
  );
}

function NavDropdown({ label, avatar, badge, items, align = 'left', active = false }) {
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
          open || active
            ? 'bg-brand-50 text-brand-800 dark:bg-brand-900/40 dark:text-brand-300'
            : 'text-ink-700 hover:bg-ink-100/70 dark:text-slate-300 dark:hover:bg-slate-800'
        }`}
        aria-expanded={open}
        aria-haspopup="menu"
        onClick={() => setOpen((v) => !v)}
      >
        {avatar && (
          <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-700 text-xs font-bold text-white">
            {avatar}
          </span>
        )}
        {label}
        {badge > 0 && (
          <span className="absolute -right-0.5 -top-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-600 text-[10px] font-bold text-white">
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
          className={`absolute top-full z-30 mt-1.5 min-w-[12rem] rounded-xl border border-ink-100 bg-white/95 py-1 shadow-lift backdrop-blur-sm dark:border-slate-700 dark:bg-slate-800 ${
            align === 'right' ? 'right-0' : 'left-0'
          }`}
        >
          {items.map((item, idx) => {
            if (item.divider) {
              return <hr key={`d-${idx}`} className="my-1 border-ink-100 dark:border-slate-700" />;
            }
            if (item.onClick) {
              return (
                <button
                  key={item.label}
                  type="button"
                  role="menuitem"
                  className="block w-full px-4 py-2 text-left text-sm text-ink-800 hover:bg-ink-50 dark:text-slate-300 dark:hover:bg-slate-700"
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
                      ? 'bg-brand-50 font-semibold text-brand-800 dark:bg-brand-900/30 dark:text-brand-300'
                      : 'text-ink-800 hover:bg-ink-50 dark:text-slate-300 dark:hover:bg-slate-700'
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
        <p className="px-3 pb-1 text-xs font-semibold uppercase tracking-wide text-ink-700/45 dark:text-slate-500">
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
  const { organization, isOrgAdmin, isOrgContentManager, isOrgModerator } = useOrganization();
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
    { to: '/media', label: t('nav.media') },
    { to: '/search', label: t('nav.search') },
    { to: '/quizzes', label: t('nav.quizzes'), auth: true },
    { to: '/forum', label: t('nav.forum') },
    { to: '/engage', label: t('nav.engage'), auth: true },
    { to: '/tutor', label: t('nav.tutor'), auth: true },
    ...(user ? [{ to: '/dashboard', label: t('nav.dashboard') }] : []),
  ].filter((link) => !link.auth || user);

  const learnMenuItems = learnLinks.map(({ to, label }) => ({ to, label }));
  const learnNavActive = learnLinks.some(
    ({ to }) => location.pathname === to || location.pathname.startsWith(`${to}/`),
  );

  const manageItems = [];
  if (hasRole('admin', 'editor') || isOrgContentManager) {
    manageItems.push({ to: '/articles/manage', label: t('nav.manageArticles') });
    manageItems.push({ to: '/media/manage', label: t('nav.manageMedia') });
    manageItems.push({ to: '/quizzes/manage', label: t('nav.manageQuizzes') });
  }
  if (hasRole('admin', 'moderator') || isOrgModerator) {
    manageItems.push({
      to: '/admin',
      label: isPlatformAdmin() ? t('nav.platformAdmin') : t('nav.moderation'),
    });
  }

  const orgItems = isOrgAdmin
    ? [
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

  const isHome = location.pathname === '/';
  const isAuthSurface =
    /^\/(login|register|forgot-password|reset-password|sso\/callback)/.test(location.pathname) ||
    location.pathname.startsWith('/invite') ||
    location.pathname.startsWith('/verify-email');

  return (
    <div className="flex min-h-screen flex-col">
      {/* Skip to content – accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-xl focus:bg-brand-700 focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-white focus:shadow-lg"
      >
        {t('a11y.skipToContent')}
      </a>

      {/* Route loading bar */}
      {routeLoading && <div className="route-loading-bar" />}

      <OfflineBanner />
      <EmailVerifyBanner />
      <InstallPrompt />
      <PushNotificationPrompt />
      <QuotaBanner />

      <header className="glass-nav" role="banner">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3.5">
          <Link to="/" className="flex min-w-0 shrink items-center gap-2.5" aria-label={t('app.name')}>
            {organization?.logo_url ? (
              <img
                src={organization.logo_url}
                alt={organization.name}
                className="h-9 w-9 shrink-0 rounded-xl object-cover ring-1 ring-ink-100 dark:ring-slate-700"
              />
            ) : (
              <PlatformLogo className="h-9 w-9" alt={organization?.name ?? t('app.name')} />
            )}
            <span className="min-w-0">
              <span className="block truncate font-display text-base font-semibold text-ink-900 dark:text-slate-100 lg:text-lg">
                {organization?.name ?? t('app.name')}
              </span>
              {organization?.name && !isAuthSurface && (
                <span className="hidden truncate text-[11px] font-medium uppercase tracking-wide text-ink-700/45 dark:text-slate-500 xl:block">
                  {t('app.tagline')}
                </span>
              )}
            </span>
          </Link>

          {!isAuthSurface && (
            <nav className="hidden items-center gap-0.5 lg:flex" aria-label="Primary">
              <NavLink to="/articles" className={navLinkClass}>
                {t('nav.articles')}
              </NavLink>
              <NavDropdown
                label={t('nav.learn')}
                items={learnMenuItems.filter((item) => item.to !== '/articles')}
                active={learnNavActive && !location.pathname.startsWith('/articles')}
              />
              <NavDropdown label={t('nav.manage')} items={manageItems} />
              <NavDropdown label={t('nav.organization')} items={orgItems} />
            </nav>
          )}

          {!isAuthSurface && (
            <>
              <HeaderSearchLink />
              <HeaderSearch />
            </>
          )}

          <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">
            {user && !isAuthSurface && <OrgSwitcher />}
            <LanguageSwitcher />

            {/* Dark mode toggle */}
            <button
              type="button"
              aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
              className="rounded-xl border border-ink-200 p-2 text-ink-700 hover:bg-ink-100/70 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800"
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

            {!isAuthSurface && (
            <button
              type="button"
              className="rounded-xl border border-ink-200 p-2 text-ink-700 dark:border-slate-600 dark:text-slate-300 lg:hidden"
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
            )}
          </div>
        </div>

        {menuOpen && !isAuthSurface && (
          <div className="border-t border-ink-100/80 bg-white/95 px-4 py-4 backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/95 lg:hidden">
            <div className="flex flex-col gap-2">
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
                    if (item.divider) return <hr key={`d-${idx}`} className="my-1 border-ink-100 dark:border-slate-700" />;
                    if (item.onClick) {
                      return (
                        <button
                          key={item.label}
                          type="button"
                          className="rounded-xl px-3 py-2 text-left text-sm font-medium text-ink-700 hover:bg-ink-100/70 dark:text-slate-300 dark:hover:bg-slate-800"
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
                            <span className="flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-red-600 px-1 text-[10px] font-bold text-white">
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
                <div className="mt-3 flex gap-2 border-t border-ink-100 pt-3 dark:border-slate-700">
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

      <main
        id="main-content"
        tabIndex={-1}
        className={
          isHome || isAuthSurface
            ? 'w-full flex-1 outline-none'
            : 'mx-auto w-full max-w-6xl flex-1 px-4 py-9 outline-none sm:py-11'
        }
      >
        <div
          className="sr-only"
          role="status"
          aria-live="polite"
          aria-atomic="true"
        >
          {location.pathname}
        </div>
        <div key={location.pathname} className={isHome || isAuthSurface ? undefined : 'page-enter'}>
          <Outlet />
        </div>
      </main>

      {!isAuthSurface && (
      <footer
        className="border-t border-ink-100/80 bg-white/60 py-11 backdrop-blur-sm dark:border-slate-800 dark:bg-ink-950/70"
        role="contentinfo"
      >
        <div className="mx-auto max-w-6xl px-4">
          <div className="flex flex-col items-center gap-5 sm:flex-row sm:justify-between">
            <div>
              <p className="font-display text-sm font-semibold text-ink-900 dark:text-slate-100">
                {t('app.name')}
              </p>
              <p className="mt-1 text-sm text-ink-700/60 dark:text-slate-500">
                © {new Date().getFullYear()}. {t('app.tagline')}.
              </p>
            </div>
            <nav
              className="flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm font-medium text-ink-700/70 dark:text-slate-400 sm:justify-end"
              aria-label={t('a11y.footerNav')}
            >
              <Link to="/articles" className="transition-colors hover:text-brand-700 dark:hover:text-brand-300">
                {t('footer.articles')}
              </Link>
              <Link to="/engage" className="transition-colors hover:text-brand-700 dark:hover:text-brand-300">
                {t('footer.engage')}
              </Link>
              <Link to="/privacy" className="transition-colors hover:text-brand-700 dark:hover:text-brand-300">
                {t('footer.privacy')}
              </Link>
              <Link to="/terms" className="transition-colors hover:text-brand-700 dark:hover:text-brand-300">
                {t('footer.terms')}
              </Link>
              <Link to="/contact" className="transition-colors hover:text-brand-700 dark:hover:text-brand-300">
                {t('footer.contact')}
              </Link>
            </nav>
          </div>
        </div>
      </footer>
      )}

      {/* Back to top */}
      {showTop && (
        <button
          type="button"
          aria-label={t('a11y.backToTop')}
          className="fixed bottom-6 right-6 z-40 flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-700 text-white shadow-lift transition-all hover:bg-brand-800"
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        >
          <ArrowUp className="h-5 w-5" />
        </button>
      )}

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3500,
          style: {
            fontSize: '0.875rem',
            maxWidth: '360px',
            borderRadius: '12px',
            fontFamily: 'Poppins, system-ui, sans-serif',
          },
          success: { iconTheme: { primary: '#047857', secondary: '#fff' } },
          error: { iconTheme: { primary: '#dc2626', secondary: '#fff' } },
        }}
      />
    </div>
  );
}
