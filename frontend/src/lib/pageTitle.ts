type Translate = (key: string) => string;

const TITLE_RULES: Array<[RegExp, string]> = [
  [/^\/articles\/manage/, 'nav.manageArticles'],
  [/^\/articles\/new/, 'nav.manageArticles'],
  [/^\/articles\/[^/]+\/edit/, 'nav.manageArticles'],
  [/^\/articles/, 'nav.articles'],
  [/^\/courses\/manage/, 'nav.manageCourses'],
  [/^\/courses\/new/, 'nav.manageCourses'],
  [/^\/courses\/[^/]+\/edit/, 'nav.manageCourses'],
  [/^\/courses/, 'nav.courses'],
  [/^\/news\/manage/, 'nav.manageNews'],
  [/^\/news\/new/, 'nav.manageNews'],
  [/^\/news\/[^/]+\/edit/, 'nav.manageNews'],
  [/^\/news/, 'nav.news'],
  [/^\/events\/manage/, 'nav.manageEvents'],
  [/^\/events\/new/, 'nav.manageEvents'],
  [/^\/events\/[^/]+\/edit/, 'nav.manageEvents'],
  [/^\/events/, 'nav.events'],
  [/^\/media\/manage/, 'nav.manageMedia'],
  [/^\/media\/new/, 'nav.manageMedia'],
  [/^\/media\/[^/]+\/edit/, 'nav.manageMedia'],
  [/^\/media/, 'nav.media'],
  [/^\/quizzes\/manage/, 'nav.manageQuizzes'],
  [/^\/quizzes\/new/, 'nav.manageQuizzes'],
  [/^\/quizzes\/results/, 'quizzes.results'],
  [/^\/quizzes\/certificates/, 'quizzes.certificates'],
  [/^\/quizzes\/[^/]+\/edit/, 'nav.manageQuizzes'],
  [/^\/quizzes/, 'nav.quizzes'],
  [/^\/engage\/manage/, 'nav.manageEngage'],
  [/^\/engage\/[^/]+\/new/, 'nav.manageEngage'],
  [/^\/engage\/[^/]+\/[^/]+\/edit/, 'nav.manageEngage'],
  [/^\/engage/, 'nav.engage'],
  [/^\/categories\/manage/, 'nav.manage'],
  [/^\/forum/, 'nav.forum'],
  [/^\/awareness/, 'nav.awareness'],
  [/^\/map/, 'nav.map'],
  [/^\/search/, 'nav.search'],
  [/^\/tutor/, 'nav.tutor'],
  [/^\/dashboard/, 'nav.dashboard'],
  [/^\/leaderboard/, 'nav.leaderboard'],
  [/^\/billing/, 'nav.billing'],
  [/^\/admin/, 'nav.admin'],
  [/^\/organization/, 'nav.organization'],
  [/^\/profile/, 'nav.profile'],
  [/^\/saved/, 'nav.saved'],
  [/^\/notifications/, 'nav.notifications'],
  [/^\/login/, 'nav.login'],
  [/^\/register/, 'nav.register'],
  [/^\/forgot-password/, 'auth.resetRequestTitle'],
  [/^\/reset-password/, 'auth.resetTitle'],
  [/^\/verify-email/, 'auth.verifying'],
  [/^\/invite/, 'saas.inviteTitle'],
  [/^\/privacy/, 'legal.privacy.title'],
  [/^\/terms/, 'legal.terms.title'],
  [/^\/contact/, 'legal.contact.title'],
  [/^\/sso\/callback/, 'nav.login'],
];

export function titleKeyForPath(pathname: string): string | null {
  const path = pathname.split('?')[0] || '/';
  if (path === '/') return 'nav.home';
  for (const [pattern, key] of TITLE_RULES) {
    if (pattern.test(path)) return key;
  }
  return null;
}

export function documentTitle(pathname: string, t: Translate): string {
  const app = t('app.name');
  const key = titleKeyForPath(pathname);
  if (!key || key === 'nav.home') {
    return `${app} — ${t('app.tagline')}`;
  }
  return `${t(key)} · ${app}`;
}
