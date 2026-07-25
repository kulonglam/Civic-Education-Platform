import i18n from '../i18n';
import { normalizeLanguage } from '../i18n/languages';

function contentLangKey() {
  return normalizeLanguage(i18n.language);
}

export const queryKeys = {
  categories: () => ['categories', contentLangKey()],
  articles: (params) => ['articles', contentLangKey(), params],
  article: (id) => ['article', contentLangKey(), id],
  forumTopics: (params) => ['forum', 'topics', params],
  forumTopic: (id) => ['forum', 'topic', id],
  notifications: (params) => ['notifications', params],
  notificationsUnread: ['notifications', 'unread'],
  quizzes: (params) => ['quizzes', contentLangKey(), params],
  quiz: (id) => ['quiz', contentLangKey(), id],
  quizResults: (params) => ['quiz-results', contentLangKey(), params],
  certificates: (params) => ['certificates', contentLangKey(), params],
  organization: ['organization'],
  orgMembers: ['organization', 'members'],
  myOrganizations: ['organization', 'mine'],
  billing: ['billing'],
  plans: ['plans'],
  orgDashboard: (filters) => ['dashboard', filters],
  orgProgress: (filters) => ['dashboard', 'progress', filters],
  myLearning: ['dashboard', 'me'],
  articlesManage: ['articles', 'manage'],
  categoriesManage: ['categories', 'manage'],
  quizzesManage: ['quizzes', 'manage'],
  media: (params) => ['media', contentLangKey(), params],
  mediaItem: (id) => ['media', contentLangKey(), id],
  mediaManage: ['media', 'manage'],
  quizEdit: (id) => ['quizzes', 'edit', id],
  tutorUsage: ['tutor', 'usage'],
  tutorHistory: ['tutor', 'history'],
  search: (q) => ['search', q],
  gamificationMe: ['gamification', 'me'],
  engagementPolls: ['engagement', 'polls'],
  engagementPetitions: ['engagement', 'petitions'],
  engagementCampaigns: ['engagement', 'campaigns'],
  adminOverview: ['admin', 'overview'],
  adminQuizzes: ['admin', 'quizzes'],
  adminForum: ['admin', 'forum'],
  adminPending: ['admin', 'pending'],
};
