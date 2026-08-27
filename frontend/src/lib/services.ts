import { api } from './api';
import type {
  AnswerCheck,
  AnalyticsForumStats,
  AnalyticsLearningInsights,
  AnalyticsOverview,
  AnalyticsPollOpinion,
  AnalyticsQuizStat,
  ApiResponse,
  Article,
  ArticleWritePayload,
  AuditLog,
  AwarenessOverview,
  AwarenessReport,
  AwarenessReportPayload,
  BillingSnapshot,
  Bookmark,
  Branding,
  Campaign,
  CampaignWritePayload,
  Category,
  Certificate,
  CheckoutResponse,
  CivicEvent,
  CivicNews,
  Course,
  CourseWritePayload,
  EventWritePayload,
  ForumComment,
  ForumReport,
  ForumTopic,
  ForumTopicWrite,
  GamificationMe,
  Id,
  InvitePreview,
  LeaderboardResponse,
  LoginResponse,
  MapCivicResponse,
  MediaAsset,
  MediaWritePayload,
  Membership,
  MfaSetupResponse,
  MyLearningSummary,
  NewsWritePayload,
  Notification,
  Organization,
  OrganizationInvite,
  OrgDashboard,
  OrgProgress,
  Paginated,
  Petition,
  PetitionWritePayload,
  Plan,
  PlatformOrgSnapshot,
  PlatformUsageSummary,
  Poll,
  PollWritePayload,
  PortalResponse,
  ProfileUpdatePayload,
  PushStats,
  QueryParams,
  Quiz,
  QuizAttemptResult,
  QuizWritePayload,
  RecommendationList,
  RegisterPayload,
  RegisterResponse,
  ScimToken,
  SearchResults,
  SecurityEvent,
  SloMetrics,
  SmsHistoryItem,
  SsoConfig,
  SupportCase,
  TokenRefreshResponse,
  TutorChatResponse,
  TutorHistoryItem,
  TutorSession,
  TutorUsage,
  UploadResult,
  User,
} from '../types/api';

export const authService = {
  register: (payload: RegisterPayload) => api.post<RegisterResponse>('/auth/register/', payload),
  login: (email: string, password: string) =>
    api.post<LoginResponse>('/auth/login/', { email, password }),
  logout: (refresh?: string | null) => api.post<void>('/auth/logout/', refresh ? { refresh } : {}),
  refreshSession: () => api.post<TokenRefreshResponse>('/auth/token/refresh/', {}),
  ssoStatus: (org: string) =>
    api.get<{ configured: boolean; enabled_for_org: boolean }>('/auth/sso/status/', {
      params: { org },
    }),
  verifyEmail: (token: string) => api.get(`/auth/verify-email/${token}/`),
  resendVerification: () => api.post('/auth/verify-email/resend/'),
  sendPhoneVerify: () => api.post('/auth/phone/verify/send/'),
  confirmPhoneVerify: (code: string) => api.post('/auth/phone/verify/confirm/', { code }),
  requestReset: (email: string) => api.post('/auth/password/reset/', { email }),
  requestResetOtp: (phone: string) => api.post('/auth/password/reset/otp/', { phone }),
  confirmResetOtp: (phone: string, code: string, password: string) =>
    api.post('/auth/password/reset/otp/confirm/', { phone, code, password }),
  confirmReset: (uid: string, token: string, password: string) =>
    api.post('/auth/password/reset/confirm/', { uid, token, password }),
  changePassword: (current_password: string, new_password: string) =>
    api.post('/auth/password/change/', { current_password, new_password }),
  mfaSetup: () => api.get<MfaSetupResponse>('/auth/mfa/setup/'),
  mfaConfirmSetup: (code: string) => api.post('/auth/mfa/setup/', { code }),
  verifyMfaLogin: (mfa_token: string, code: string) =>
    api.post<LoginResponse>('/auth/mfa/verify/', { mfa_token, code }),
};

export const userService = {
  profile: () => api.get<User>('/users/profile/'),
  updateProfile: (payload: ProfileUpdatePayload) => api.put<User>('/users/profile/', payload),
  uploadAvatar: (file: File) => {
    const formData = new FormData();
    formData.append('avatar', file);
    return api.patch<User>('/users/profile/avatar/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: () => api.get<Paginated<User>>('/users/'),
  suspend: (userId: Id) => api.post(`/users/${userId}/suspend/`),
  unsuspend: (userId: Id) => api.post(`/users/${userId}/unsuspend/`),
  updateRole: (userId: Id, role: string) => api.patch<User>(`/users/${userId}/role/`, { role }),
  exportMyData: () => api.get('/users/me/export/'),
  deactivate: () => api.post('/users/me/deactivate/'),
};

export const platformService = {
  branding: () => api.get<Branding>('/branding/'),
};

export const articleService = {
  list: (params?: QueryParams) => api.get<Paginated<Article>>('/articles/', { params }),
  get: (id: Id | undefined) => api.get<Article>(`/articles/${id}/`),
  create: (payload: ArticleWritePayload) => api.post<Article>('/articles/', payload),
  update: (id: Id | undefined, payload: Partial<ArticleWritePayload>) =>
    api.patch<Article>(`/articles/${id}/`, payload),
  remove: (id: Id | undefined) => api.delete(`/articles/${id}/`),
  approve: (id: Id | undefined) => api.post(`/articles/${id}/approve/`),
  reject: (id: Id | undefined) => api.post(`/articles/${id}/reject/`),
  uploadAttachment: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<UploadResult>('/articles/attachments/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  uploadImage: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<UploadResult>('/articles/images/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  recordProgress: (id: Id | undefined, payload: Record<string, unknown>) =>
    api.post(`/articles/${id}/progress/`, payload),
};

export const mediaService = {
  list: (params?: QueryParams) => api.get<Paginated<MediaAsset>>('/media/', { params }),
  get: (id: Id | undefined) => api.get<MediaAsset>(`/media/${id}/`),
  create: (payload: MediaWritePayload) => api.post<MediaAsset>('/media/', payload),
  update: (id: Id | undefined, payload: Partial<MediaWritePayload>) =>
    api.patch<MediaAsset>(`/media/${id}/`, payload),
  remove: (id: Id | undefined) => api.delete(`/media/${id}/`),
  uploadAudio: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<UploadResult>('/media/audio/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  uploadVideo: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<UploadResult>('/media/video/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  recordProgress: (id: Id | undefined, payload: Record<string, unknown>) =>
    api.post(`/media/${id}/progress/`, payload),
};

export const categoryService = {
  list: () => api.get<Paginated<Category>>('/categories/'),
  create: (payload: Partial<Category>) => api.post<Category>('/categories/', payload),
  update: (id: Id | undefined, payload: Partial<Category>) => api.patch<Category>(`/categories/${id}/`, payload),
  remove: (id: Id | undefined) => api.delete(`/categories/${id}/`),
};

export const quizService = {
  list: (params?: QueryParams) => api.get<Paginated<Quiz>>('/quizzes/', { params }),
  get: (id: Id | undefined) => api.get<Quiz>(`/quizzes/${id}/`),
  create: (payload: QuizWritePayload) => api.post<Quiz>('/quizzes/', payload),
  update: (id: Id | undefined, payload: Partial<QuizWritePayload>) =>
    api.patch<Quiz>(`/quizzes/${id}/`, payload),
  remove: (id: Id | undefined) => api.delete(`/quizzes/${id}/`),
  attempt: (id: Id | undefined, answers: Record<string, string>) =>
    api.post<QuizAttemptResult>(`/quizzes/${id}/attempt/`, { answers }),
  checkAnswer: (id: Id | undefined, questionId: Id, answer: string) =>
    api.post<AnswerCheck>(`/quizzes/${id}/check-answer/`, { question_id: questionId, answer }),
  results: (params?: QueryParams) =>
    api.get<Paginated<QuizAttemptResult>>('/quizzes/results/', { params }),
  certificates: (params?: QueryParams) =>
    api.get<Paginated<Certificate>>('/quizzes/certificates/', { params }),
  downloadCertificate: (id: Id | undefined) =>
    api.get<{ download_url?: string }>(`/quizzes/certificates/${id}/download/`),
};

export const forumService = {
  listTopics: (params?: QueryParams) => api.get<Paginated<ForumTopic>>('/topics/', { params }),
  getTopic: (id: Id | undefined) => api.get<ForumTopic>(`/topics/${id}/`),
  createTopic: (payload: ForumTopicWrite) => api.post<ForumTopic>('/topics/', payload),
  addComment: (topicId: Id, comment: string) =>
    api.post<ForumComment>(`/topics/${topicId}/comments/`, { comment }),
  moderateTopic: (id: Id | undefined, is_approved: boolean) =>
    api.patch(`/topics/${id}/moderate/`, { is_approved }),
  moderateComment: (id: Id | undefined, is_approved: boolean) =>
    api.patch(`/comments/${id}/moderate/`, { is_approved }),
  lockTopic: (id: Id | undefined, is_locked: boolean) => api.patch(`/topics/${id}/lock/`, { is_locked }),
  acceptAnswer: (id: Id | undefined, comment_id: Id) =>
    api.post(`/topics/${id}/accept-answer/`, { comment_id }),
  reportTopic: (id: Id | undefined, payload: Record<string, unknown>) =>
    api.post(`/topics/${id}/report/`, payload),
  reportComment: (id: Id | undefined, payload: Record<string, unknown>) =>
    api.post(`/comments/${id}/report/`, payload),
  reviewReport: (id: Id | undefined, payload: Record<string, unknown>) =>
    api.patch(`/topics/reports/${id}/`, payload),
  pending: () =>
    api.get<{ topics?: ForumTopic[]; comments?: ForumComment[]; reports?: ForumReport[] }>(
      '/topics/pending/',
    ),
};

export const notificationService = {
  list: (params?: QueryParams) => api.get<Paginated<Notification>>('/notifications/', { params }),
  broadcast: (payload: Record<string, unknown>) => api.post('/notifications/broadcast/', payload),
  subscribePush: (subscription: PushSubscriptionJSON) =>
    api.post('/notifications/push/subscribe/', subscription),
  unsubscribePush: (subscription: PushSubscriptionJSON) =>
    api.delete('/notifications/push/subscribe/', { data: subscription }),
  pushStats: () => api.get<PushStats>('/notifications/push/stats/'),
  pushCleanup: () => api.post<{ message?: string }>('/notifications/push/cleanup/'),
  markRead: (id: Id | undefined) => api.patch(`/notifications/${id}/read/`),
  markAllRead: () => api.patch('/notifications/read-all/'),
};

export const auditService = {
  logs: (params?: QueryParams) => api.get<Paginated<AuditLog>>('/audit/logs/', { params }),
  export: (params?: QueryParams) =>
    api.get<Blob>('/audit/logs/export/', { params, responseType: 'blob' }),
};

export const securityService = {
  events: (params?: QueryParams) =>
    api.get<Paginated<SecurityEvent>>('/security/events/', { params }),
};

export const analyticsService = {
  overview: () => api.get<AnalyticsOverview>('/analytics/overview/'),
  quizzes: () => api.get<AnalyticsQuizStat[]>('/analytics/quizzes/'),
  forum: () => api.get<AnalyticsForumStats>('/analytics/forum/'),
  polls: () => api.get<AnalyticsPollOpinion>('/analytics/polls/'),
  learning: () => api.get<AnalyticsLearningInsights>('/analytics/learning/'),
  dashboard: (params?: QueryParams) => api.get<OrgDashboard>('/analytics/dashboard/', { params }),
  progress: (params?: QueryParams) => api.get<OrgProgress>('/analytics/progress/', { params }),
  exportCsv: (params?: QueryParams) =>
    api.get<Blob>('/analytics/export/csv/', { params, responseType: 'blob' }),
  exportReportPdf: (params?: QueryParams) =>
    api.get<Blob>('/analytics/export/report.pdf/', { params, responseType: 'blob' }),
  me: () => api.get<MyLearningSummary>('/analytics/me/'),
};

export const organizationService = {
  current: () => api.get<Organization>('/organization/current/'),
  mine: () => api.get<Paginated<Membership>>('/organization/mine/'),
  update: (payload: Partial<Organization>) =>
    api.patch<Organization>('/organization/current/', payload),
  bySlug: (slug: string) => api.get<Organization>(`/organization/by-slug/${slug}/`),
  members: (params?: QueryParams) =>
    api.get<Paginated<Membership>>('/organization/members/', { params }),
  invite: (email: string, role = 'member', departmentId: Id | null = null) =>
    api.post<Membership | OrganizationInvite>('/organization/members/invite/', {
      email,
      role,
      ...(departmentId ? { department_id: departmentId } : {}),
    }),
  bulkImport: (payload: FormData | Record<string, unknown>) =>
    api.post('/organization/members/bulk-import/', payload),
  pendingInvites: () => api.get<Paginated<OrganizationInvite>>('/organization/invites/'),
  revokeInvite: (inviteId: Id) => api.delete(`/organization/invites/${inviteId}/`),
  invitePreview: (token: string) =>
    api.get<InvitePreview>(`/organization/invites/preview/${token}/`),
  acceptInvite: (token: string) => api.post(`/organization/invites/accept/${token}/`),
  updateMemberRole: (membershipId: Id, role: string, departmentId?: Id | null) =>
    api.patch<Membership>(`/organization/members/${membershipId}/`, {
      role,
      ...(departmentId !== undefined ? { department_id: departmentId } : {}),
    }),
  removeMember: (membershipId: Id) => api.delete(`/organization/members/${membershipId}/`),
  leave: () => api.post('/organization/leave/'),
  departments: () => api.get<Paginated<{ id: Id; name: string; slug?: string }>>('/organization/departments/'),
  createDepartment: (payload: { name: string }) => api.post('/organization/departments/', payload),
  deleteDepartment: (id: Id | undefined) => api.delete(`/organization/departments/${id}/`),
  getSso: () => api.get<SsoConfig>('/organization/sso/'),
  updateSso: (payload: Partial<SsoConfig>) => api.put<SsoConfig>('/organization/sso/', payload),
  scimTokens: () => api.get<Paginated<ScimToken>>('/organization/scim/tokens/'),
  createScimToken: (name: string) => api.post<ScimToken>('/organization/scim/tokens/', { name }),
  revokeScimToken: (id: Id | undefined) => api.delete(`/organization/scim/tokens/${id}/`),
  compliancePack: () => api.get<Blob>('/organization/compliance/pack/', { responseType: 'blob' }),
  verifyAudit: () => api.get('/organization/compliance/verify/'),
  supportCases: () => api.get<Paginated<SupportCase>>('/organization/support/cases/'),
  createSupportCase: (payload: { subject?: string; body?: string; priority?: string }) =>
    api.post<SupportCase>('/organization/support/cases/', payload),
  closeSupportCase: (id: Id | undefined, status = 'closed') =>
    api.patch(`/organization/support/cases/${id}/`, { status }),
  platformOrgs: (params?: QueryParams) =>
    api.get<Paginated<PlatformOrgSnapshot>>('/organization/platform/orgs/', { params }),
  platformOrgDetail: (orgId: Id) =>
    api.get<PlatformOrgSnapshot>(`/organization/platform/orgs/${orgId}/`),
  setOrgActive: (orgId: Id, is_active: boolean) =>
    api.patch<PlatformOrgSnapshot>(`/organization/platform/orgs/${orgId}/`, { is_active }),
  assignOrgPlan: (orgId: Id, planCode: string) =>
    api.post<PlatformOrgSnapshot>(`/organization/platform/orgs/${orgId}/plan/`, { plan_code: planCode }),
  platformUsage: () => api.get<PlatformUsageSummary>('/organization/platform/usage/'),
  platformSupportCases: (params?: QueryParams) =>
    api.get<Paginated<SupportCase>>('/organization/platform/support/cases/', { params }),
  updatePlatformSupportCase: (id: Id | undefined, payload: Record<string, unknown>) =>
    api.patch(`/organization/platform/support/cases/${id}/`, payload),
  platformSlo: () => api.get<SloMetrics>('/organization/platform/slo/'),
  impersonate: (orgId: Id, userId: Id) =>
    api.post<LoginResponse>(`/organization/platform/orgs/${orgId}/impersonate/`, {
      user_id: userId,
    }),
  exitImpersonation: () => api.post<LoginResponse>('/organization/platform/impersonate/exit/'),
};

export const billingService = {
  plans: () => api.get<Paginated<Plan>>('/billing/plans/'),
  subscription: () => api.get<BillingSnapshot>('/billing/subscription/'),
  checkout: (planCode: string) =>
    api.post<CheckoutResponse>('/billing/checkout/', { plan_code: planCode }),
  portal: () => api.post<PortalResponse>('/billing/portal/'),
};

export const tutorService = {
  chat: (message: string, articleId?: Id) =>
    api.post<TutorChatResponse>('/tutor/chat/', {
      message,
      ...(articleId ? { article_id: articleId } : {}),
    }),
  getSession: () => api.get<TutorSession>('/tutor/chat/session/'),
  clearSession: () => api.delete('/tutor/chat/session/'),
  history: () => api.get<TutorHistoryItem[] | Paginated<TutorHistoryItem>>('/tutor/chat/history/'),
  historyDetail: (sessionId: Id) =>
    api.get<TutorHistoryItem>(`/tutor/chat/history/${sessionId}/`),
  usage: () => api.get<TutorUsage>('/tutor/usage/'),
};

export const gamificationService = {
  me: () => api.get<GamificationMe>('/gamification/me/'),
  leaderboard: (params?: QueryParams) =>
    api.get<LeaderboardResponse>('/gamification/leaderboard/', { params }),
};

export const recommendationService = {
  list: () => api.get<RecommendationList>('/recommendations/'),
};

export const mapService = {
  civic: () => api.get<MapCivicResponse>('/maps/civic/'),
};

export const bookmarkService = {
  list: (params?: QueryParams) => api.get<Paginated<Bookmark>>('/bookmarks/', { params }),
  toggleArticle: (id: Id | undefined) => api.post<Bookmark>(`/articles/${id}/bookmark/`),
  toggleMedia: (id: Id | undefined) => api.post<Bookmark>(`/media/${id}/bookmark/`),
  remove: (id: Id | undefined) => api.delete(`/bookmarks/${id}/`),
};

export const engagementService = {
  polls: (params?: QueryParams) => api.get<Paginated<Poll>>('/engagement/polls/', { params }),
  getPoll: (id: Id | undefined) => api.get<Poll>(`/engagement/polls/${id}/`, { params: { manage: '1' } }),
  createPoll: (payload: PollWritePayload) => api.post<Poll>('/engagement/polls/', payload),
  updatePoll: (id: Id | undefined, payload: Partial<PollWritePayload>) =>
    api.patch<Poll>(`/engagement/polls/${id}/`, payload),
  removePoll: (id: Id | undefined) => api.delete(`/engagement/polls/${id}/`),
  votePoll: (pollId: Id, optionId: Id) =>
    api.post(`/engagement/polls/${pollId}/vote/`, { option_id: optionId }),
  petitions: (params?: QueryParams) =>
    api.get<Paginated<Petition>>('/engagement/petitions/', { params }),
  getPetition: (id: Id | undefined) =>
    api.get<Petition>(`/engagement/petitions/${id}/`, { params: { manage: '1' } }),
  createPetition: (payload: PetitionWritePayload) =>
    api.post<Petition>('/engagement/petitions/', payload),
  updatePetition: (id: Id | undefined, payload: Partial<PetitionWritePayload>) =>
    api.patch<Petition>(`/engagement/petitions/${id}/`, payload),
  removePetition: (id: Id | undefined) => api.delete(`/engagement/petitions/${id}/`),
  signPetition: (petitionId: Id) => api.post(`/engagement/petitions/${petitionId}/sign/`),
  campaigns: (params?: QueryParams) =>
    api.get<Paginated<Campaign>>('/engagement/campaigns/', { params }),
  getCampaign: (id: Id | undefined) =>
    api.get<Campaign>(`/engagement/campaigns/${id}/`, { params: { manage: '1' } }),
  createCampaign: (payload: CampaignWritePayload) =>
    api.post<Campaign>('/engagement/campaigns/', payload),
  updateCampaign: (id: Id | undefined, payload: Partial<CampaignWritePayload>) =>
    api.patch<Campaign>(`/engagement/campaigns/${id}/`, payload),
  removeCampaign: (id: Id | undefined) => api.delete(`/engagement/campaigns/${id}/`),
  joinCampaign: (campaignId: Id) => api.post(`/engagement/campaigns/${campaignId}/join/`),
};

export const courseService = {
  list: (params?: QueryParams) => api.get<Paginated<Course>>('/courses/', { params }),
  get: (id: Id | undefined, params?: QueryParams) => api.get<Course>(`/courses/${id}/`, { params }),
  create: (payload: CourseWritePayload) => api.post<Course>('/courses/', payload),
  update: (id: Id | undefined, payload: Partial<CourseWritePayload>) =>
    api.patch<Course>(`/courses/${id}/`, payload),
  remove: (id: Id | undefined) => api.delete(`/courses/${id}/`),
};

export const newsService = {
  list: (params?: QueryParams) => api.get<Paginated<CivicNews>>('/news/', { params }),
  get: (id: Id | undefined) => api.get<CivicNews>(`/news/${id}/`),
  create: (payload: NewsWritePayload) => api.post<CivicNews>('/news/', payload),
  update: (id: Id | undefined, payload: Partial<NewsWritePayload>) =>
    api.patch<CivicNews>(`/news/${id}/`, payload),
  remove: (id: Id | undefined) => api.delete(`/news/${id}/`),
};

export const eventsService = {
  list: (params?: QueryParams) => api.get<Paginated<CivicEvent>>('/events/', { params }),
  get: (id: Id | undefined) => api.get<CivicEvent>(`/events/${id}/`),
  create: (payload: EventWritePayload) => api.post<CivicEvent>('/events/', payload),
  update: (id: Id | undefined, payload: Partial<EventWritePayload>) =>
    api.patch<CivicEvent>(`/events/${id}/`, payload),
  remove: (id: Id | undefined) => api.delete(`/events/${id}/`),
  register: (id: Id | undefined, registered: boolean) =>
    api.post<CivicEvent>(`/events/${id}/register/`, { registered }),
  reminder: (id: Id | undefined, reminder: boolean) =>
    api.post<CivicEvent>(`/events/${id}/reminder/`, { reminder }),
  calendar: (id: Id | undefined) => api.get<Blob>(`/events/${id}/calendar/`, { responseType: 'blob' }),
};

export const awarenessService = {
  overview: () => api.get<AwarenessOverview>('/awareness/'),
  report: (payload: AwarenessReportPayload) =>
    api.post<AwarenessReport>('/awareness/reports/', payload),
  listReports: (params?: QueryParams) =>
    api.get<Paginated<AwarenessReport>>('/awareness/reports/', { params }),
  reviewReport: (id: Id | undefined, payload: { status?: string; moderator_notes?: string }) =>
    api.patch(`/awareness/reports/${id}/`, payload),
};

export const searchService = {
  query: (q: string, limit = 8) => api.get<SearchResults>('/search/', { params: { q, limit } }),
};

export const notifyService = {
  sendSms: (payload: Record<string, unknown>) => api.post('/notify/sms/', payload),
  broadcast: (message: string) => api.post('/notify/broadcast/', { message }),
  platformBroadcast: (message: string) =>
    api.post<{ message?: string }>('/notify/broadcast/platform/', { message }),
  history: () => api.get<Paginated<SmsHistoryItem> | SmsHistoryItem[]>('/notify/history/'),
  whatsappBroadcast: (message: string) => api.post('/notify/whatsapp/broadcast/', { message }),
  platformWhatsAppBroadcast: (message: string) =>
    api.post<{ message?: string }>('/notify/whatsapp/broadcast/platform/', { message }),
  whatsappHistory: () =>
    api.get<Paginated<SmsHistoryItem> | SmsHistoryItem[]>('/notify/whatsapp/history/'),
};

export type { ApiResponse };
