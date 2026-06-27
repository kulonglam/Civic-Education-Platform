import { api } from "./api";
const authService = {
  register: (payload) => api.post("/auth/register/", payload),
  login: (email, password) => api.post("/auth/login/", { email, password }),
  logout: (refresh) => api.post("/auth/logout/", { refresh }),
  ssoStatus: (org) => api.get("/auth/sso/status/", { params: { org } }),
  verifyEmail: (token) => api.get(`/auth/verify-email/${token}/`),
  resendVerification: () => api.post("/auth/verify-email/resend/"),
  sendPhoneVerify: () => api.post("/auth/phone/verify/send/"),
  confirmPhoneVerify: (code) => api.post("/auth/phone/verify/confirm/", { code }),
  requestReset: (email) => api.post("/auth/password/reset/", { email }),
  requestResetOtp: (phone) => api.post("/auth/password/reset/otp/", { phone }),
  confirmResetOtp: (phone, code, password) =>
    api.post("/auth/password/reset/otp/confirm/", { phone, code, password }),
  confirmReset: (uid, token, password) => api.post("/auth/password/reset/confirm/", { uid, token, password }),
  changePassword: (current_password, new_password) =>
    api.post("/auth/password/change/", { current_password, new_password }),
  mfaSetup: () => api.get("/auth/mfa/setup/"),
  mfaConfirmSetup: (code) => api.post("/auth/mfa/setup/", { code }),
  verifyMfaLogin: (mfa_token, code) => api.post("/auth/mfa/verify/", { mfa_token, code }),
};
const userService = {
  profile: () => api.get("/users/profile/"),
  updateProfile: (payload) => api.put("/users/profile/", payload),
  uploadAvatar: (file) => {
    const formData = new FormData();
    formData.append("avatar", file);
    return api.patch("/users/profile/avatar/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  list: () => api.get("/users/"),
  suspend: (userId) => api.post(`/users/${userId}/suspend/`),
  unsuspend: (userId) => api.post(`/users/${userId}/unsuspend/`),
  updateRole: (userId, role) => api.patch(`/users/${userId}/role/`, { role }),
};
const articleService = {
  list: (params) => api.get("/articles/", { params }),
  get: (id) => api.get(`/articles/${id}/`),
  create: (payload) => api.post("/articles/", payload),
  update: (id, payload) => api.patch(`/articles/${id}/`, payload),
  remove: (id) => api.delete(`/articles/${id}/`),
  uploadAttachment: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/articles/attachments/upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};
const categoryService = {
  list: () => api.get("/categories/"),
  create: (payload) => api.post("/categories/", payload),
  update: (id, payload) => api.patch(`/categories/${id}/`, payload),
  remove: (id) => api.delete(`/categories/${id}/`),
};
const quizService = {
  list: (params) => api.get("/quizzes/", { params }),
  get: (id) => api.get(`/quizzes/${id}/`),
  create: (payload) => api.post("/quizzes/", payload),
  update: (id, payload) => api.patch(`/quizzes/${id}/`, payload),
  remove: (id) => api.delete(`/quizzes/${id}/`),
  attempt: (id, answers) => api.post(`/quizzes/${id}/attempt/`, { answers }),
  results: (params) => api.get("/quizzes/results/", { params }),
  certificates: (params) => api.get("/quizzes/certificates/", { params }),
  downloadCertificate: (id) => api.get(`/quizzes/certificates/${id}/download/`)
};
const forumService = {
  listTopics: (params) => api.get("/topics/", { params }),
  getTopic: (id) => api.get(`/topics/${id}/`),
  createTopic: (payload) => api.post("/topics/", payload),
  addComment: (topicId, comment) => api.post(`/topics/${topicId}/comments/`, { comment }),
  moderateTopic: (id, is_approved) => api.patch(`/topics/${id}/moderate/`, { is_approved }),
  moderateComment: (id, is_approved) => api.patch(`/comments/${id}/moderate/`, { is_approved }),
  pending: () => api.get("/topics/pending/")
};
const notificationService = {
  list: (params) => api.get("/notifications/", { params }),
  broadcast: (payload) => api.post("/notifications/broadcast/", payload),
  subscribePush: (subscription) => api.post("/notifications/push/subscribe/", subscription),
  unsubscribePush: (subscription) =>
    api.delete("/notifications/push/subscribe/", { data: subscription }),
  pushStats: () => api.get("/notifications/push/stats/"),
  pushCleanup: () => api.post("/notifications/push/cleanup/"),
  markRead: (id) => api.patch(`/notifications/${id}/read/`),
  markAllRead: () => api.patch("/notifications/read-all/"),
};
const auditService = {
  logs: (params) => api.get("/audit/logs/", { params }),
};
const analyticsService = {
  overview: () => api.get("/analytics/overview/"),
  quizzes: () => api.get("/analytics/quizzes/"),
  forum: () => api.get("/analytics/forum/"),
  learning: () => api.get("/analytics/learning/"),
  dashboard: (params) => api.get("/analytics/dashboard/", { params }),
  progress: (params) => api.get("/analytics/progress/", { params }),
  exportCsv: (params) =>
    api.get("/analytics/export/csv/", { params, responseType: "blob" })
};
const organizationService = {
  current: () => api.get("/organization/current/"),
  mine: () => api.get("/organization/mine/"),
  update: (payload) => api.patch("/organization/current/", payload),
  bySlug: (slug) => api.get(`/organization/by-slug/${slug}/`),
  members: () => api.get("/organization/members/"),
  invite: (email, role = "member") => api.post("/organization/members/invite/", { email, role }),
  pendingInvites: () => api.get("/organization/invites/"),
  revokeInvite: (inviteId) => api.delete(`/organization/invites/${inviteId}/`),
  invitePreview: (token) => api.get(`/organization/invites/preview/${token}/`),
  acceptInvite: (token) => api.post(`/organization/invites/accept/${token}/`),
  updateMemberRole: (membershipId, role) => api.patch(`/organization/members/${membershipId}/`, { role }),
  removeMember: (membershipId) => api.delete(`/organization/members/${membershipId}/`),
  leave: () => api.post("/organization/leave/")
};
const billingService = {
  plans: () => api.get("/billing/plans/"),
  subscription: () => api.get("/billing/subscription/"),
  checkout: (planCode) => api.post("/billing/checkout/", { plan_code: planCode }),
  portal: () => api.post("/billing/portal/")
};
const tutorService = {
  chat: (message, articleId) =>
    api.post("/tutor/chat/", {
      message,
      ...(articleId ? { article_id: articleId } : {}),
    }),
  clearSession: () => api.delete("/tutor/chat/session/"),
  usage: () => api.get("/tutor/usage/"),
};
const notifyService = {
  sendSms: (payload) => api.post("/notify/sms/", payload),
  broadcast: (message) => api.post("/notify/broadcast/", { message }),
  platformBroadcast: (message) => api.post("/notify/broadcast/platform/", { message }),
  history: () => api.get("/notify/history/"),
};
export {
  analyticsService,
  articleService,
  auditService,
  authService,
  billingService,
  categoryService,
  forumService,
  notificationService,
  notifyService,
  organizationService,
  quizService,
  tutorService,
  userService
};
