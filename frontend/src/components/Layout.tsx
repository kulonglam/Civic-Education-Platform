import { useCallback, useEffect, useRef, useState, type KeyboardEvent as ReactKeyboardEvent, type ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import toast, { Toaster } from 'react-hot-toast';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, NavLink, Outlet, useLocation, useNavigate, type NavLinkRenderProps } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useOrganization } from '../context/OrganizationContext';
import { useDarkMode } from '../hooks/useDarkMode';
import { AccessibilityMenu } from './AccessibilityMenu';
import { LanguageSwitcher } from './LanguageSwitcher';
import { OrgSwitcher } from './OrgSwitcher';
import { QuotaBanner } from './QuotaBanner';
import { OfflineBanner } from './OfflineBanner';
import { ApiWakeBanner } from './ApiWakeBanner';
import { EmailVerifyBanner } from './EmailVerifyBanner';
import { InstallPrompt } from './InstallPrompt';
import { PushNotificationPrompt } from './PushNotificationPrompt';
import { ArrowUp, Moon, Sun } from './Icons';
import { notificationService } from '../lib/services';
import { queryKeys } from '../lib/queryKeys';
import { extractError, tokenStore } from '../lib/api';
import { stopSpeaking } from '../lib/speech';
import { PlatformLogo } from './PlatformLogo';
import { documentTitle } from '../lib/pageTitle';
import { useNotificationSocket } from '../hooks/useNotificationSocket';
import { ErrorBoundary } from './ErrorBoundary';

function navLinkClass({ isActive }: NavLinkRenderProps) {
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
      className="icon-btn hidden lg:inline-flex xl:hidden"
      aria-label={t('nav.search')}
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <circle cx="11" cy="11" r="8" />
        <path d="M21 21l-4.35-4.35" />
      </svg>
    </Link>
  );
}

function NavDropdown({
  label,
  avatar = null,
  badge = null,
  items,
  align = 'left',
  active = false,
  compactOnMobile = false,
}: {
  label: string;
  avatar?: ReactNode;
  badge?: number | null;
  items: any[];
  align?: 'left' | 'right';
  active?: boolean;
  compactOnMobile?: boolean;
}) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return undefined;
    const close = (e: MouseEvent) => {
      if (ref.current && e.target instanceof Node && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', close);
    return () => document.removeEventListener('mousedown', close);
  }, [open]);

  const focusItem = (index: number) => {
    const nodes = ref.current?.querySelectorAll<HTMLElement>('[role="menuitem"]');
    if (!nodes?.length) return;
    const next = (index + nodes.length) % nodes.length;
    nodes[next].focus();
  };

  const handleKeyDown = (e: ReactKeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Escape') {
      setOpen(false);
      e.currentTarget.querySelector('button')?.focus();
      return;
    }
    if (!open && (e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' ')) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setOpen(true);
        window.setTimeout(() => focusItem(0), 0);
      }
      return;
    }
    if (!open) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      const nodes = [...(ref.current?.querySelectorAll<HTMLElement>('[role="menuitem"]') ?? [])];
      const index = nodes.indexOf(document.activeElement as HTMLElement);
      focusItem(index + 1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      const nodes = [...(ref.current?.querySelectorAll<HTMLElement>('[role="menuitem"]') ?? [])];
      const index = nodes.indexOf(document.activeElement as HTMLElement);
      focusItem(index <= 0 ? nodes.length - 1 : index - 1);
    } else if (e.key === 'Home') {
      e.preventDefault();
      focusItem(0);
    } else if (e.key === 'End') {
      e.preventDefault();
      const nodes = ref.current?.querySelectorAll<HTMLElement>('[role="menuitem"]');
      if (nodes?.length) focusItem(nodes.length - 1);
    }
  };

  if (items.length === 0) return null;

  const triggerLabel = (badge ?? 0) > 0 ? `${label}, ${t('a11y.unreadCount', { count: badge })}` : label;

  return (
    <div ref={ref} className="relative" onKeyDown={handleKeyDown}>
      <button
        type="button"
        className={`relative flex min-h-11 max-w-[40vw] items-center gap-1.5 rounded-lg px-2 py-2 text-sm font-medium transition-colors sm:max-w-none sm:px-3 ${
          open || active
            ? 'bg-brand-50 text-brand-800 dark:bg-brand-900/40 dark:text-brand-300'
            : 'text-ink-700 hover:bg-ink-100/70 dark:text-slate-300 dark:hover:bg-slate-800'
        }`}
        aria-expanded={open}
        aria-haspopup="menu"
        aria-label={triggerLabel}
        onClick={() => setOpen((v) => !v)}
      >
        {avatar && (
          <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-700 text-xs font-bold text-white">
            {avatar}
          </span>
        )}
        {label && (
          <span className={compactOnMobile ? 'hidden max-w-[8rem] truncate sm:inline' : 'truncate'}>
            {label}
          </span>
        )}
        {(badge ?? 0) > 0 && (
          <span className="absolute -right-0.5 -top-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-600 text-[10px] font-bold text-white">
            {(badge ?? 0) > 9 ? '9+' : badge}
          </span>
        )}
        <svg className="hidden sm:block" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
          <path d="M6 9l6 6 6-6" />
        </svg>
      </button>

      {open && (
        <div
          role="menu"
          className={`absolute top-full z-30 mt-1.5 max-h-[70vh] min-w-[12rem] max-w-[min(20rem,calc(100vw-1.5rem))] overflow-y-auto rounded-xl border border-ink-100 bg-white/95 py-1 shadow-lift backdrop-blur-sm dark:border-slate-700 dark:bg-slate-800 ${
            align === 'right' ? 'end-0' : 'start-0'
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

function MobileSection({ title, children }: { title?: string; children?: ReactNode }) {
  if (!children) return null;
  return (
    <div className="pt-2">
      {title && (
        <p className="px-3 pb-1 text-xs font-semibold uppercase tracking-wide text-ink-700/70 dark:text-slate-500">
          {title}
        </p>
      )}
      <div className="flex flex-col gap-1">{children}</div>
    </div>
  );
}

export function Layout() {
  const { t } = useTranslation();
  const { user, logout, hasRole, isPlatformAdmin, impersonation, exitImpersonation } = useAuth();
  const { organization, isOrgAdmin, isOrgContentManager, isOrgModerator } = useOrganization();
  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient();
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

  useEffect(() => {
    document.title = documentTitle(location.pathname, t);
  }, [location.pathname, t]);

  // Back-to-top visibility
  useEffect(() => {
    const onScroll = () => setShowTop(window.scrollY > 400);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Close mobile menu on navigation
  useEffect(() => {
    setMenuOpen(false);
    stopSpeaking();
  }, [location.pathname]);

  useEffect(() => {
    if (!menuOpen) return undefined;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setMenuOpen(false);
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [menuOpen]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Unread notifications count (only when logged in, refreshed every 3 min)
  const onLiveNotification = useCallback((payload: { title?: string; message?: string }) => {
    toast(payload.title || payload.message || t('notifications.title'));
    queryClient.invalidateQueries({ queryKey: queryKeys.notificationsUnread });
    queryClient.invalidateQueries({ queryKey: ['notifications'] });
  }, [queryClient, t]);

  const liveNotifications = useNotificationSocket({
    enabled: Boolean(user),
    token: tokenStore.access ?? undefined,
    onNotification: onLiveNotification,
  });

  const { data: unreadCount = 0 } = useQuery({
    queryKey: queryKeys.notificationsUnread,
    queryFn: async () => {
      const { data } = await notificationService.list({ page: '1' });
      return (data.results ?? []).filter((n) => !n.is_read).length;
    },
    enabled: !!user,
    staleTime: 3 * 60 * 1000,
    refetchInterval: liveNotifications ? false : 3 * 60 * 1000,
  });

  const learnLinks = [
    { to: '/articles', label: t('nav.articles') },
    { to: '/courses', label: t('nav.courses') },
    { to: '/news', label: t('nav.news') },
    { to: '/events', label: t('nav.events') },
    { to: '/map', label: t('nav.map') },
    { to: '/awareness', label: t('nav.awareness') },
    { to: '/media', label: t('nav.media') },
    { to: '/search', label: t('nav.search') },
    { to: '/quizzes', label: t('nav.quizzes') },
    { to: '/forum', label: t('nav.forum') },
    { to: '/engage', label: t('nav.engage'), auth: true },
    { to: '/tutor', label: t('nav.tutor'), auth: true },
    ...(user ? [{ to: '/saved', label: t('nav.saved') }] : []),
    ...(user ? [{ to: '/dashboard', label: t('nav.dashboard') }] : []),
    ...(user ? [{ to: '/leaderboard', label: t('nav.leaderboard') }] : []),
  ].filter((link) => !link.auth || user);

  const learnMenuItems = learnLinks.map(({ to, label }) => ({ to, label }));
  const learnNavActive = learnLinks.some(
    ({ to }) => location.pathname === to || location.pathname.startsWith(`${to}/`),
  );

  const manageItems: { to: string; label: string }[] = [];
  if (hasRole('admin', 'editor') || isOrgContentManager) {
    manageItems.push({ to: '/articles/manage', label: t('nav.manageArticles') });
    manageItems.push({ to: '/news/manage', label: t('nav.manageNews') });
    manageItems.push({ to: '/events/manage', label: t('nav.manageEvents') });
    manageItems.push({ to: '/media/manage', label: t('nav.manageMedia') });
    manageItems.push({ to: '/quizzes/manage', label: t('nav.manageQuizzes') });
    manageItems.push({ to: '/courses/manage', label: t('nav.manageCourses') });
    manageItems.push({ to: '/engage/manage', label: t('nav.manageEngage') });
  }
  if (hasRole('admin', 'moderator', 'editor') || isOrgModerator || isOrgContentManager || isOrgAdmin) {
    manageItems.push({
      to: '/admin',
      label: isPlatformAdmin() ? t('nav.platformAdmin') : t('nav.admin'),
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
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-[max(1rem,env(safe-area-inset-top))] focus:z-50 focus:rounded-xl focus:bg-brand-700 focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-white focus:shadow-lg"
      >
        {t('a11y.skipToContent')}
      </a>

      {/* Route loading bar */}
      {routeLoading && <div className="route-loading-bar" aria-hidden="true" />}

      <ApiWakeBanner />
      <OfflineBanner />
      <EmailVerifyBanner />
      <InstallPrompt />
      <PushNotificationPrompt />
      <QuotaBanner />
      {impersonation && (
        <div className="bg-amber-500 px-4 py-2 text-center text-sm text-ink-900">
          <span>
            {t('admin.impersonationBanner', {
              name: impersonation.targetName || impersonation.targetEmail,
              actor: impersonation.actorEmail,
            })}
          </span>
          <button
            type="button"
            className="ml-3 font-semibold underline"
            onClick={async () => {
              try {
                await exitImpersonation();
                navigate('/admin');
              } catch (err) {
                toast.error(extractError(err));
              }
            }}
          >
            {t('admin.exitImpersonation')}
          </button>
        </div>
      )}

      <header className="glass-nav" role="banner">
        <div className="mx-auto flex max-w-6xl min-w-0 items-center justify-between gap-2 px-3 py-3 sm:gap-3 sm:px-4 sm:py-3.5">
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
              <span className="block truncate font-display text-sm font-semibold text-ink-900 dark:text-slate-100 sm:text-base lg:text-lg">
                {organization?.name ?? t('app.name')}
              </span>
              {organization?.name && !isAuthSurface && (
                <span className="hidden truncate text-[11px] font-medium uppercase tracking-wide text-ink-700/70 dark:text-slate-500 xl:block">
                  {t('app.tagline')}
                </span>
              )}
            </span>
          </Link>

          {!isAuthSurface && (
            <nav className="hidden items-center gap-0.5 lg:flex" aria-label={t('a11y.primaryNav')}>
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

          <div className="flex shrink-0 items-center gap-1 sm:gap-1.5">
            {user && !isAuthSurface && <OrgSwitcher />}
            <LanguageSwitcher />
            <AccessibilityMenu />

            <button
              type="button"
              aria-label={dark ? t('a11y.switchToLight') : t('a11y.switchToDark')}
              className="icon-btn"
              onClick={() => setDark((d) => !d)}
            >
              {dark ? <Sun className="h-4 w-4" aria-hidden="true" /> : <Moon className="h-4 w-4" aria-hidden="true" />}
            </button>

            {user ? (
              <NavDropdown
                label={user.first_name || ''}
                avatar={user.first_name?.charAt(0).toUpperCase()}
                badge={unreadCount}
                items={accountItems}
                align="right"
                compactOnMobile
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
              className="icon-btn lg:hidden"
              onClick={() => setMenuOpen((v) => !v)}
              aria-label={t('a11y.menu')}
              aria-expanded={menuOpen}
              aria-controls="mobile-nav"
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
          <div
            id="mobile-nav"
            className="max-h-[min(70vh,28rem)] overflow-y-auto border-t border-ink-100/80 bg-white/95 px-4 py-4 backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/95 lg:hidden"
          >
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
                      <NavLink key={item.to} to={item.to || '/'} className={navLinkClass}>
                        <span className="flex items-center justify-between">
                          {item.label}
                          {(item.badge ?? 0) > 0 && (
                            <span className="flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-red-600 px-1 text-[10px] font-bold text-white">
                              {(item.badge ?? 0) > 99 ? '99+' : item.badge}
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
          {documentTitle(location.pathname, t)}
        </div>
        <div key={location.pathname} className={isHome || isAuthSurface ? undefined : 'page-enter'}>
          <ErrorBoundary resetKey={location.pathname}>
            <Outlet />
          </ErrorBoundary>
        </div>
      </main>

      {!isAuthSurface && (
      <footer
        className="border-t border-ink-100/80 bg-white/60 py-11 backdrop-blur-sm dark:border-slate-800 dark:bg-ink-950/70"
        style={{ paddingBottom: 'max(2.75rem, env(safe-area-inset-bottom))' }}
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
              <Link to="/news" className="transition-colors hover:text-brand-700 dark:hover:text-brand-300">
                {t('footer.news')}
              </Link>
              <Link to="/events" className="transition-colors hover:text-brand-700 dark:hover:text-brand-300">
                {t('footer.events')}
              </Link>
              <Link to="/awareness" className="transition-colors hover:text-brand-700 dark:hover:text-brand-300">
                {t('footer.awareness')}
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
          className="fixed bottom-[max(1.25rem,env(safe-area-inset-bottom))] end-4 z-40 flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-700 text-white shadow-lift transition-all hover:bg-brand-800 sm:bottom-6 sm:end-6"
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        >
          <ArrowUp className="h-5 w-5" />
        </button>
      )}

      <Toaster
        position="top-center"
        containerStyle={{ top: 'max(0.75rem, env(safe-area-inset-top))' }}
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
