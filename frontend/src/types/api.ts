import type { AxiosError, AxiosResponse } from 'axios';

export type Id = string;
export type QueryParams = Record<string, string | number | boolean | undefined | null>;
export type ApiError = AxiosError;

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type ApiResponse<T> = Promise<AxiosResponse<T>>;

export function unwrapList<T>(data: Paginated<T> | T[] | null | undefined): T[] {
  if (!data) return [];
  return Array.isArray(data) ? data : (data.results ?? []);
}

export function unwrapCount<T>(data: Paginated<T> | T[] | null | undefined): number {
  if (!data) return 0;
  if (Array.isArray(data)) return data.length;
  return data.count ?? data.results?.length ?? 0;
}

export type Role = {
  id?: Id;
  name?: string;
};

export type UserProfile = {
  bio?: string;
  avatar_url?: string;
  preferred_language?: string;
  region?: string;
  age_band?: string;
  show_on_leaderboard?: boolean;
};

export type User = {
  id: Id;
  email: string;
  phone?: string | null;
  first_name?: string;
  last_name?: string;
  role?: Role | null;
  is_active?: boolean;
  is_suspended?: boolean;
  email_verified?: boolean;
  phone_verified?: boolean;
  created_at?: string;
  profile?: UserProfile | null;
  avatar_url?: string;
  mfa_required?: boolean;
  mfa_enabled?: boolean;
  last_activity_at?: string | null;
  impersonator_email?: string | null;
  whatsapp_alerts?: boolean;
};

export type LoginResponse = {
  access?: string;
  refresh?: string;
  user?: User;
  mfa_required?: boolean;
  mfa_token?: string;
  mfa_setup_required?: boolean;
  actor?: { email?: string };
  target?: { email?: string; full_name?: string };
  detail?: string;
};

export type TokenRefreshResponse = {
  access: string;
  refresh?: string;
};

export type RegisterPayload = {
  email: string;
  password: string;
  password_confirm?: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  account_type?: string;
  organization_name?: string;
  invite_token?: string;
};

export type RegisterResponse = {
  user?: User;
  email_sent?: boolean;
  message?: string;
};

export type ProfileUpdatePayload = {
  first_name?: string;
  last_name?: string;
  phone?: string;
  bio?: string;
  avatar_url?: string;
  preferred_language?: string;
  region?: string;
  age_band?: string;
  show_on_leaderboard?: boolean;
  whatsapp_alerts?: boolean;
};

export type MfaSetupResponse = {
  secret?: string;
  otpauth_url?: string;
  qr_png?: string;
};

export type Organization = {
  id: Id;
  name: string;
  slug: string;
  tagline?: string;
  logo_url?: string;
  primary_color?: string;
  is_active?: boolean;
  force_mfa_for_admins?: boolean;
  audit_retention_days?: number;
  ip_allowlist?: string[];
  created_at?: string;
};

export type Department = {
  id: Id;
  name: string;
  slug?: string;
  created_at?: string;
};

export type Membership = {
  id: Id;
  user?: Id;
  user_email?: string;
  user_name?: string;
  user_phone?: string | null;
  role: string;
  department?: Department | null;
  created_at?: string;
  organization?: Organization;
};

export type OrganizationInvite = {
  id: Id;
  email: string;
  role?: string;
  department?: Department | null;
  organization_name?: string;
  created_at?: string;
  expires_at?: string;
  accepted_at?: string | null;
};

export type InvitePreview = {
  email: string;
  role?: string;
  is_expired?: boolean;
  organization: {
    name?: string;
    slug?: string;
  };
};

export type SsoConfig = {
  id?: Id;
  enabled: boolean;
  issuer: string;
  client_id: string;
  client_secret?: string;
  scopes: string;
  has_client_secret?: boolean;
  is_ready?: boolean;
  updated_at?: string;
};

export type SupportCase = {
  id: Id;
  subject?: string;
  body?: string;
  status?: string;
  priority?: string;
  organization_name?: string;
  created_at?: string;
};

export type Category = {
  id: Id;
  name: string;
  slug: string;
  description?: string;
  name_ar?: string;
  description_ar?: string;
  is_locked?: boolean;
};

export type MediaSummary = {
  id: Id;
  title: string;
  title_ar?: string;
  media_type?: string;
  source?: string;
  file_url?: string;
  external_url?: string;
  playback_url?: string;
  mime_type?: string;
  duration_seconds?: number | null;
  thumbnail_url?: string;
  captions_url?: string;
  status?: string;
  category_name?: string;
  published_at?: string | null;
};

export type MediaAsset = MediaSummary & {
  description?: string;
  description_ar?: string;
  category?: Category | null;
  author?: Id;
  author_name?: string;
  published_at?: string | null;
  created_at?: string;
  updated_at?: string;
  is_bookmarked?: boolean;
};

export type MediaWritePayload = {
  title: string;
  title_ar?: string;
  description?: string;
  description_ar?: string;
  media_type: string;
  source: string;
  file_url?: string;
  external_url?: string;
  mime_type?: string;
  thumbnail_url?: string;
  captions_url?: string;
  category_id?: Id | '' | null;
  status: string;
};

export type Article = {
  id: Id;
  title: string;
  title_ar?: string;
  content?: string;
  content_ar?: string;
  source_language?: string;
  translation_status?: string;
  translated_at?: string | null;
  translation_fingerprint?: string;
  category?: Category | null;
  author?: Id;
  author_name?: string;
  tags?: string[] | string;
  featured_image_url?: string;
  attachment_url?: string;
  attachment_name?: string;
  attachment_version?: string;
  document_label?: string;
  is_controlled_document?: boolean;
  audio_media?: MediaSummary | null;
  video_media?: MediaSummary | null;
  status?: string;
  reviewed_by?: Id | null;
  reviewed_by_name?: string | null;
  reviewed_at?: string | null;
  published_at?: string | null;
  created_at?: string;
  updated_at?: string;
  is_bookmarked?: boolean;
};

export type ArticleWritePayload = {
  title: string;
  title_ar?: string;
  content?: string;
  content_ar?: string;
  category_id: Id | '';
  tags?: string[];
  featured_image_url?: string;
  attachment_url?: string;
  attachment_name?: string;
  attachment_version?: string;
  document_label?: string;
  is_controlled_document?: boolean;
  audio_media_id?: Id | '' | null;
  video_media_id?: Id | '' | null;
  status: string;
};

export type ArticleFormState = {
  title: string;
  title_ar: string;
  content: string;
  content_ar: string;
  category_id: string;
  tags: string;
  featured_image_url: string;
  attachment_url: string;
  attachment_name: string;
  attachment_version: string;
  document_label: string;
  is_controlled_document: boolean;
  audio_media_id: string;
  video_media_id: string;
  status: string;
};

export type Question = {
  id?: Id;
  question_text?: string;
  question_text_ar?: string;
  question_type?: string;
  options?: string[];
  options_ar?: string[];
  correct_answer?: string;
  explanation?: string;
  explanation_ar?: string;
  option_feedback?: Array<string | { en?: string; ar?: string }>;
  points?: number;
  order?: number;
  displayOptions?: Array<{ value: string; label: string }>;
};

export type Quiz = {
  id: Id;
  title: string;
  title_ar?: string;
  description?: string;
  description_ar?: string;
  passing_score?: number;
  kind?: string;
  feedback_mode?: string;
  max_attempts?: number | null;
  issues_certificate?: boolean;
  is_active?: boolean;
  question_count?: number;
  created_at?: string;
  questions?: Question[];
};

export type QuizWritePayload = {
  title: string;
  title_ar?: string;
  description?: string;
  description_ar?: string;
  passing_score: number;
  kind?: string;
  feedback_mode?: string;
  max_attempts?: number | null;
  is_active?: boolean;
  questions?: Question[];
};

export type QuizQuestionForm = {
  question_text: string;
  question_text_ar: string;
  question_type: string;
  optionsText: string;
  optionsTextAr: string;
  correct_answer: string;
  explanation: string;
  explanation_ar: string;
  optionFeedback: string[];
  optionFeedbackAr: string[];
  points: number;
  order: number;
};

export type QuizFormState = {
  title: string;
  title_ar: string;
  description: string;
  description_ar: string;
  passing_score: number;
  kind: string;
  feedback_mode: string;
  max_attempts: string | number;
  is_active: boolean;
  questions: QuizQuestionForm[];
};

export type QuizAttemptResult = {
  id?: Id;
  quiz?: Id;
  quiz_title?: string;
  score?: number;
  max_score?: number;
  passed?: boolean;
  attempted_at?: string;
  queued?: boolean;
  data?: QuizAttemptResult;
  review?: Array<{
    question_id: string;
    question_type?: string;
    question_text?: string;
    learner_answer?: string;
    correct_answer?: string;
    is_correct?: boolean;
    points?: number;
    points_awarded?: number;
    explanation?: string;
  }>;
};

export type AnswerCheck = {
  is_correct?: boolean;
  correct_answer?: string;
  explanation?: string;
};

export type Certificate = {
  id: Id;
  certificate_number?: string;
  quiz?: Id;
  quiz_title?: string;
  issue_date?: string;
  pdf_url?: string;
};

export type CourseLesson = {
  id: Id;
  article_id?: Id;
  title?: string;
  title_ar?: string;
  sort_order?: number;
  completed?: boolean;
};

export type Course = {
  id: Id;
  title: string;
  title_ar?: string;
  slug?: string;
  description?: string;
  description_ar?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
  lessons?: CourseLesson[];
  lesson_count?: number;
  completed_count?: number;
};

export type CourseWritePayload = {
  title: string;
  title_ar?: string;
  slug?: string;
  description?: string;
  description_ar?: string;
  status: string;
  lesson_ids: Id[];
};

export type CourseFormState = {
  title: string;
  title_ar: string;
  slug: string;
  description: string;
  description_ar: string;
  status: string;
  lesson_ids: Id[];
};

export type PollOption = {
  id?: Id;
  label: string;
  label_ar?: string;
  sort_order?: number;
  vote_count?: number;
};

export type Poll = {
  id: Id;
  question: string;
  question_ar?: string;
  description?: string;
  description_ar?: string;
  kind?: string;
  status?: string;
  closes_at?: string | null;
  is_open?: boolean;
  options?: PollOption[];
  user_vote_option_id?: string | null;
  total_votes?: number;
  results_visible?: boolean;
  created_at?: string;
};

export type PollWritePayload = {
  question: string;
  question_ar?: string;
  description?: string;
  description_ar?: string;
  kind?: string;
  status?: string;
  options: PollOption[];
};

export type Petition = {
  id: Id;
  title: string;
  title_ar?: string;
  description?: string;
  description_ar?: string;
  goal_signatures?: number;
  signature_count?: number;
  goal_reached?: boolean;
  user_signed?: boolean;
  status?: string;
  created_at?: string;
};

export type PetitionWritePayload = {
  title: string;
  title_ar?: string;
  description?: string;
  description_ar?: string;
  goal_signatures: number;
  status?: string;
};

export type Campaign = {
  id: Id;
  title: string;
  title_ar?: string;
  description?: string;
  description_ar?: string;
  link_url?: string;
  status?: string;
  created_at?: string;
  signup_count?: number;
  user_joined?: boolean;
};

export type CampaignWritePayload = {
  title: string;
  title_ar?: string;
  description?: string;
  description_ar?: string;
  link_url?: string;
  status?: string;
};

export type CivicNews = {
  id: Id;
  title: string;
  title_ar?: string;
  body?: string;
  body_ar?: string;
  topic?: string;
  claim_type?: string;
  source_name?: string;
  source_url?: string;
  status?: string;
  published_at?: string | null;
  created_at?: string;
  updated_at?: string;
  created_by_name?: string | null;
};

export type NewsWritePayload = {
  title: string;
  title_ar?: string;
  body?: string;
  body_ar?: string;
  topic: string;
  claim_type: string;
  source_name?: string;
  source_url?: string;
  status: string;
};

export type CivicEvent = {
  id: Id;
  title: string;
  title_ar?: string;
  description?: string;
  description_ar?: string;
  location?: string;
  location_ar?: string;
  kind?: string;
  starts_at?: string;
  ends_at?: string | null;
  is_all_day?: boolean;
  status?: string;
  allows_registration?: boolean;
  capacity?: number | null;
  source_name?: string;
  source_url?: string;
  created_at?: string;
  updated_at?: string;
  created_by_name?: string | null;
  registered_count?: number;
  spots_left?: number | null;
  user_registered?: boolean;
  user_reminder?: boolean;
  google_calendar_url?: string;
  is_cancelled?: boolean;
  region?: string;
  latitude?: number | null;
  longitude?: number | null;
};

export type EventWritePayload = {
  title: string;
  title_ar?: string;
  description?: string;
  description_ar?: string;
  location?: string;
  location_ar?: string;
  kind: string;
  starts_at?: string | null;
  ends_at?: string | null;
  is_all_day?: boolean;
  allows_registration?: boolean;
  capacity?: number | null;
  source_name?: string;
  source_url?: string;
  status: string;
  region?: string;
};

export type EventFormState = {
  title: string;
  title_ar: string;
  description: string;
  description_ar: string;
  location: string;
  location_ar: string;
  kind: string;
  starts_at: string;
  ends_at: string;
  is_all_day: boolean;
  allows_registration: boolean;
  capacity: string;
  source_name: string;
  source_url: string;
  status: string;
  region: string;
};

export type AwarenessReport = {
  id: Id;
  channel: string;
  description: string;
  source_url?: string;
  reporter_contact?: string;
  status?: string;
  moderator_notes?: string;
  reviewed_at?: string | null;
  created_at?: string;
};

export type AwarenessReportPayload = {
  channel: string;
  description: string;
  source_url?: string;
  reporter_contact?: string;
};

export type AwarenessLesson = {
  key: string;
  article_id?: Id;
};

export type AwarenessOverview = {
  lessons?: AwarenessLesson[];
  quiz?: { id: Id } | null;
};

export type ForumTopic = {
  id: Id;
  title: string;
  content?: string;
  kind?: string;
  board?: string;
  is_approved?: boolean;
  is_locked?: boolean;
  created_at?: string;
  author_name?: string;
  comment_count?: number;
  comments?: ForumComment[];
};

export type ForumComment = {
  id: Id;
  comment?: string;
  body?: string;
  is_approved?: boolean;
  created_at?: string;
  author_name?: string;
};

export type ForumTopicWrite = {
  title: string;
  content?: string;
  kind?: string;
  board?: string;
};

export type Notification = {
  id: Id;
  title?: string;
  body?: string;
  message?: string;
  notification_type?: string;
  is_read?: boolean;
  created_at?: string;
  url?: string;
};

export type Bookmark = {
  id: Id;
  kind?: 'article' | 'media' | string;
    article?: {
    id: Id;
    title: string;
    title_ar?: string;
    featured_image_url?: string;
    category_name?: string;
    published_at?: string | null;
    media_type?: string;
  } | null;
  media?: MediaSummary | null;
  created_at?: string;
  bookmarked?: boolean;
};

export type Plan = {
  id?: Id;
  code: string;
  name?: string;
  price_cents?: number;
  currency?: string;
  interval?: string;
  max_members?: number;
  max_articles?: number;
  max_quizzes?: number;
  features?: Record<string, boolean | string | number>;
};

export type UsageMeter = {
  used: number;
  limit: number | null;
};

export type BillingUsage = {
  members: UsageMeter;
  articles: UsageMeter;
  quizzes: UsageMeter;
};

export type Subscription = {
  id?: Id;
  status?: string;
  plan?: Plan | null;
};

export type BillingSnapshot = {
  subscription?: Subscription | null;
  usage?: BillingUsage;
  self_serve_checkout?: boolean;
};

export type CheckoutResponse = {
  checkout_url: string;
};

export type PortalResponse = {
  portal_url: string;
};

export type TutorMessage = {
  role: 'user' | 'assistant' | string;
  content: string;
  sources?: Array<{ title?: string; url?: string; article_id?: Id }>;
};

export type TutorChatResponse = {
  reply: string;
  sources?: TutorMessage['sources'];
  messages_used_today?: number;
  messages_remaining?: number;
  daily_limit?: number | null;
  session_message_count?: number;
};

export type TutorSession = {
  messages?: TutorMessage[];
};

export type TutorHistoryItem = {
  id: Id;
  session_id?: Id;
  title?: string;
  preview?: string;
  turns?: number;
  last_at?: string;
  created_at?: string;
  messages?: TutorMessage[];
};

export type TutorUsage = {
  messages_used_today?: number;
  messages_remaining?: number;
  daily_limit?: number | null;
  session_message_count?: number;
};

export type GamificationMe = {
  xp?: number;
  xp_points?: number;
  xp_to_next_level?: number;
  level?: number;
  badges?: Array<{ id?: Id; slug?: string; name?: string; description?: string; earned_at?: string }>;
  badges_earned?: Array<{ id?: Id; slug?: string; name?: string; description?: string }>;
};

export type LeaderboardEntry = {
  user_id?: Id;
  user_name?: string;
  display_name?: string;
  xp?: number;
  xp_points?: number;
  level?: number;
  rank?: number;
  is_me?: boolean;
  badges_earned?: number;
};

export type LeaderboardResponse = {
  me?: { rank?: number; xp_points?: number };
  results?: LeaderboardEntry[];
  entries?: LeaderboardEntry[];
};

export type RecommendationItem = {
  id: Id;
  kind: string;
  title: string;
  title_ar?: string;
  href: string;
  reason?: string;
  course_title?: string;
};

export type RecommendationList = {
  items?: RecommendationItem[];
  personalized?: boolean;
  articles?: Article[];
  quizzes?: Quiz[];
};

export type SearchResults = {
  articles?: Article[];
  media?: MediaAsset[];
  topics?: ForumTopic[];
};

export type MapCivicResponse = {
  events?: CivicEvent[];
  regions?: Array<{ id?: string; name?: string; count?: number }>;
};

export type UploadResult = {
  url: string;
  name?: string;
  attachment_url?: string;
  attachment_name?: string;
  mime_type?: string;
};

export type ScimToken = {
  id: Id;
  name?: string;
  token?: string;
  created_at?: string;
};

export type SmsHistoryItem = {
  id?: Id;
  message?: string;
  created_at?: string;
  status?: string;
};

export type Branding = {
  name?: string;
  logo_url?: string;
  primary_color?: string;
  support_email?: string;
};

export type AuditLog = {
  id: Id;
  action?: string;
  actor_email?: string;
  user_email?: string;
  user_name?: string;
  activity_type?: string;
  created_at?: string;
  timestamp?: string;
  metadata?: Record<string, unknown>;
};

export type SecurityEvent = {
  id: Id;
  event_type?: string;
  user_email?: string;
  created_at?: string;
  ip_address?: string;
};

export type AnalyticsOverview = {
  total_users: number;
  active_users_30d: number;
  articles_published: number;
  quiz_completions: number;
  lesson_completion_rate: number;
  media_completion_rate: number;
  member_completion_rate: number;
};

export type AnalyticsQuizStat = {
  quiz_id: Id;
  title: string;
  attempt_count: number;
  pass_rate: number;
  avg_score: number;
};

export type AnalyticsForumStats = {
  total_topics: number;
  total_comments: number;
  pending_topics: number;
  pending_comments: number;
};

export type AnalyticsBucket = {
  key: string;
  count: number;
};

export type AnalyticsPollOptionStat = {
  id: Id;
  label: string;
  vote_count: number;
  percent: number;
};

export type AnalyticsPollStat = {
  id: Id;
  question: string;
  kind: string;
  status: string;
  is_open: boolean;
  total_votes: number;
  options: AnalyticsPollOptionStat[];
  demographics_available: boolean;
  regions: AnalyticsBucket[];
  age_bands: AnalyticsBucket[];
};

export type AnalyticsPollOpinion = {
  total_polls: number;
  total_responses: number;
  polls: AnalyticsPollStat[];
};

export type AnalyticsCompletion = {
  published_lessons: number;
  lesson_starts: number;
  lesson_completions: number;
  lesson_completion_rate: number;
  published_media: number;
  media_starts: number;
  media_completions: number;
  media_completion_rate: number;
  members: number;
  members_completed_lesson: number;
  member_completion_rate: number;
};

export type AnalyticsPopularLesson = {
  id: Id;
  title: string;
  completions: number;
  views: number;
};

export type AnalyticsCategoryCount = {
  category: string;
  slug: string;
  article_count: number;
};

export type AnalyticsTagCount = {
  tag: string;
  count: number;
};

export type AnalyticsTranslationRow = {
  model: string;
  field: string;
  total: number;
  translated: number;
  missing: number;
  completeness_pct: number;
};

export type AnalyticsTranslation = {
  rows: AnalyticsTranslationRow[];
  overall_translated: number;
  overall_total: number;
  overall_pct: number;
};

export type AnalyticsRegionalEngagement = {
  demographics_available: boolean;
  regions: AnalyticsBucket[];
  stated_count: number;
  member_count: number;
};

export type AnalyticsLearningInsights = {
  articles_by_category: AnalyticsCategoryCount[];
  top_tags: AnalyticsTagCount[];
  completion: AnalyticsCompletion;
  popular_lessons: AnalyticsPopularLesson[];
  languages: AnalyticsBucket[];
  regional_engagement: AnalyticsRegionalEngagement;
  translation: AnalyticsTranslation;
};

export type LearningActivity = {
  type: 'article' | 'media' | 'quiz' | string;
  id: Id;
  title: string;
  completed?: boolean;
  at?: string | null;
  score?: number | null;
};

export type LearningCategoryProgress = {
  category: string;
  slug: string;
  articles_completed: number;
  articles_total: number;
  media_completed: number;
  media_total: number;
};

export type MyLearningSummary = {
  articles_completed: number;
  articles_in_progress: number;
  articles_total: number;
  media_completed: number;
  media_total: number;
  quizzes_attempted: number;
  quizzes_passed: number;
  avg_quiz_score: number;
  certificates: number;
  by_category: LearningCategoryProgress[];
  recent_activity: LearningActivity[];
};

export type OrgDashboard = {
  total_members: number;
  active_members_30d: number;
  quiz_attempts: number;
  quiz_pass_rate: number;
  certificates_issued: number;
  published_articles: number;
};

export type OrgProgressMember = {
  user_id: Id;
  email: string;
  first_name?: string;
  last_name?: string;
  role?: string;
  department?: string | null;
  department_id?: Id | null;
  quizzes_attempted: number;
  quizzes_passed: number;
  avg_score: number;
  certificates: number;
  articles_completed: number;
  media_completed: number;
  last_activity?: string | null;
};

export type OrgProgress = {
  members: OrgProgressMember[];
};

export type PushStats = {
  total_subscriptions: number;
  users_with_push: number;
  inactive_user_subscriptions: number;
  total_users: number;
  top_users?: Array<{ user__email?: string; subscriptions?: number }>;
};

export type PlatformOrgMember = {
  user_id: Id;
  email: string;
  full_name?: string;
  membership_role?: string;
  platform_role?: string | null;
  can_impersonate?: boolean;
};

export type PlatformOrgSnapshot = {
  id: Id;
  name: string;
  slug: string;
  tagline?: string;
  is_active?: boolean;
  force_mfa_for_admins?: boolean;
  audit_retention_days?: number;
  member_count?: number;
  department_count?: number;
  plan_code?: string | null;
  plan_name?: string | null;
  published_articles?: number;
  pending_review_articles?: number;
  controlled_documents?: number;
  quiz_attempts?: number;
  certificates_issued?: number;
  active_learners_30d?: number;
  members?: PlatformOrgMember[];
  created_at?: string;
};

export type PlatformUsageSummary = {
  totals: {
    organizations: number;
    active_organizations: number;
    members: number;
    published_articles: number;
    quiz_attempts: number;
    certificates: number;
    active_learners_30d: number;
  };
  organizations: PlatformOrgSnapshot[];
  generated_at?: string;
  window_start?: string;
};

export type SloMetrics = {
  generated_at?: string;
  window_hours?: number;
  targets?: {
    availability_percent?: number;
    auth_success_rate_percent?: number;
  };
  observed?: {
    auth_success_rate_percent?: number;
    login_success_24h?: number;
    login_failure_24h?: number;
    security_events_24h?: number;
    permission_denied_24h?: number;
    open_support_cases?: number;
    events_by_type?: Record<string, number>;
  };
  status?: string;
  probes?: Record<string, string>;
  notes?: string;
};

export type ForumReport = {
  id: Id;
  reason?: string;
  status?: string;
  details?: string;
  created_at?: string;
  topic?: Id;
  topic_title?: string;
  comment?: Id;
  comment_excerpt?: string;
  reporter_name?: string;
};
