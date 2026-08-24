# Graph Report - Civic Education Platform  (2026-08-24)

## Corpus Check
- 517 files · ~215,192 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3278 nodes · 7906 edges · 265 communities (177 shown, 88 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 437 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0f7f6397`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- views/mfa.py
- TopicDetailPage.jsx
- quizzes/views.py
- analytics/views.py
- sso.py
- Layout.jsx
- forum/views.py
- queryKeys.js
- conftest.py
- Icons.jsx
- bind_client_to_org
- ui.jsx
- AuthContext.jsx
- log_activity
- core/middleware.py
- event_views.py
- EventsDetailPage.jsx
- articles.js
- ArticleViewSet
- notifications/views.py
- session.py
- ArticleEditorPage.jsx
- media_views.py
- learning/views.py
- ArticleSerializer
- useAuth
- tutor/views.py
- apply_subscription_updated
- dependencies
- scim.py
- tenants/models.py
- integrations.py
- engagement/models.py
- devDependencies
- engagement/views.py
- sms_views.py
- django_db
- test_article_translation.py
- eslint
- test_product_features.py
- QuizTakePage.jsx
- Alert
- Notification
- accounts/models.py
- TutorChat
- NotificationConsumer
- CivicUser
- Command
- test_deploy.py
- tutor/services.py
- services.js
- compilerOptions
- Pre-launch checklist
- sms_providers.py
- sms_services.py
- accounts/serializers.py
- Command
- test_tutor_providers.py
- Production environment checklist — integrations
- SuspiciousContentReportSerializer
- _parse_stats
- Quiz
- TutorUnavailable
- Command
- TestAuth
- views/__init__.py
- scripts
- quizzes/serializers.py
- billing/services.py
- TestNotifications
- helpers.js
- TestPlatformSupportAndSecurity
- TestBilling
- TestForum
- TenantsConfig
- TestArticleI18n
- Load testing (Locust)
- Backend setup
- AccessibilityContext.jsx
- get_current_organization
- Command
- package.json
- AccountsConfig
- Civic Education RSS — Frontend
- LearningConfig
- 0003_migrate_primary_color_to_green.py
- enable_mfa
- Article
- TestPasswordReset
- vercel.json
- AnalyticsConfig
- AuditConfig
- ForumConfig
- NotificationsConfig
- QuizzesConfig
- TutorConfig
- Constitution & controlled documents
- django_db
- AI Tutor — RAG & PDF grounding
- make_icon
- accounts/migrations/0001_initial.py
- 0002_user_phone_phoneotp.py
- 0003_product_features.py
- 0004_userprofile_mfa.py
- accounts/migrations/0005_grade_a_enterprise.py
- audit/migrations/0001_initial.py
- 0002_activitylog_organization.py
- 0003_alter_activitylog_activity_type.py
- 0004_enterprise_gov_features.py
- audit/migrations/0005_grade_a_enterprise.py
- billing/migrations/0001_initial.py
- 0001_enterprise_gaps.py
- forum/migrations/0001_initial.py
- 0002_discussioncomment_organization_and_more.py
- learning/migrations/0001_initial.py
- 0002_alter_category_options.py
- 0003_article_organization_category_organization_and_more.py
- 0004_article_attachment.py
- 0005_alter_article_attachment_url.py
- 0006_enterprise_gov_features.py
- 0007_enterprise_gaps.py
- 0008_media_assets.py
- notifications/migrations/0001_initial.py
- 0002_notification_organization.py
- 0003_smsmessage.py
- 0004_product_features.py
- 0005_notification_preference.py
- quizzes/migrations/0001_initial.py
- 0002_alter_certificate_options_alter_quiz_options.py
- 0003_certificate_organization_quiz_organization_and_more.py
- 0004_question_options_ar.py
- tenants/migrations/0001_initial.py
- 0002_organization_invites.py
- 0004_alter_organization_primary_color.py
- 0005_enterprise_gov_features.py
- 0006_grade_a_enterprise.py
- tutor/migrations/0001_initial.py
- 0002_tutor_daily_usage.py
- wsgi.py
- Enterprise features (Government / NGO)
- get_preferred_language
- @testing-library/user-event
- Compliance readiness (SOC 2 / ISO 27001)
- Disaster recovery
- @vitejs/plugin-react
- bump_session_epoch
- TestBookmarks
- TestTopicModeration
- billing/views.py
- engagement/serializers.py
- Membership
- Civic Education RSS API Reference
- gamification/services.py
- test_tutor_retrieval.py
- Testing & CI
- TestSmsAlerts
- user_management.py
- TestUserSuspendIsolation
- jwt.js
- 0012_bookmark.py
- sso_views.py
- 0009_learning_progress.py
- 0006_phone_verified_activity_type.py
- BaseBillingProvider
- TestTenantIsolation
- BillingConfig
- tailwindcss
- @testing-library/jest-dom
- @testing-library/react
- 0005_quiz_kind_feedback_question_explanation.py
- RecordingProvider
- prompts.py
- EngagementConfig
- GamificationConfig
- profile.py
- TestTutorChat
- upload_file
- PhoneVerifyConfirmSerializer
- TestCivicNews
- TestAwareness
- globals
- @playwright/test
- start.sh
- TestGlobalSearch
- 0006_userprofile_xp_points.py
- engagement/migrations/0001_initial.py
- gamification/migrations/0001_initial.py
- 0010_article_tutor_index_text_mediaasset_captions_url.py
- broadcast_notification_task
- test_org_analytics.py
- 0011_article_translation.py
- @vitest/coverage-v8
- 0008_role_super_admin.py
- CookieTokenRefreshView
- RegisterView
- 0006_question_scenario_option_feedback.py
- Command
- TestPolls
- TestOrganizationInvites
- create_default_subscription
- 0002_civicnews.py
- 0003_suspiciouscontentreport.py
- 0003_forum_community_moderation.py
- 0007_userprofile_region_age_band.py
- 0004_poll_kind_vote_demographics.py
- core/permissions.py
- 0006_alter_notification_notification_type.py
- App.jsx
- TestLearningProgress
- 0005_civicevent_eventsignup.py
- TestMediaLibraryApi

## God Nodes (most connected - your core abstractions)
1. `bind_client_to_org()` - 146 edges
2. `get_current_organization()` - 99 edges
3. `log_activity()` - 88 edges
4. `Membership` - 75 edges
5. `extractError()` - 71 edges
6. `useAuth()` - 59 edges
7. `Article` - 50 edges
8. `formatDate()` - 41 edges
9. `Alert()` - 40 edges
10. `useOrganization()` - 38 edges

## Surprising Connections (you probably didn't know these)
- `Command` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/management/commands/seed_data.py → backend/apps/accounts/models.py
- `Command` --uses--> `UserProfile`  [INFERRED]
  backend/apps/accounts/management/commands/seed_data.py → backend/apps/accounts/models.py
- `RegisterSerializer` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/serializers.py → backend/apps/accounts/models.py
- `RoleSerializer` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/serializers.py → backend/apps/accounts/models.py
- `UserRoleUpdateSerializer` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/serializers.py → backend/apps/accounts/models.py

## Import Cycles
- None detected.

## Communities (265 total, 88 thin omitted)

### Community 0 - "views/mfa.py"
Cohesion: 0.08
Nodes (31): consume_mfa_challenge(), generate_totp_secret(), issue_mfa_challenge(), provisioning_uri(), TOTP multi-factor authentication for privileged accounts., Platform admins and organization owners/admins must use MFA when org requires…, totp_for_secret(), user_has_mfa_enabled() (+23 more)

### Community 1 - "TopicDetailPage.jsx"
Cohesion: 0.08
Nodes (16): EngagementPage, TopicDetailPage, GuestSaveCta(), engagementService, forumService, mockHasRole, mockIsPlatformAdmin, AwarenessPage() (+8 more)

### Community 2 - "quizzes/views.py"
Cohesion: 0.22
Nodes (13): CertificateSerializer, QuizAttemptSerializer, QuizAttemptSubmitSerializer, QuizCheckAnswerSerializer, QuizReviewItemSerializer, generate_certificate_number(), CertificateDownloadView, CertificateListView (+5 more)

### Community 3 - "analytics/views.py"
Cohesion: 0.07
Nodes (39): IsOrgAnalyticsAdmin, BasePermission, Organization owner or admin (analytics plan checked in the view)., build_completion_snapshot(), build_learning_insights(), build_my_learning_summary(), build_poll_opinion_summary(), build_popular_lessons() (+31 more)

### Community 4 - "sso.py"
Cohesion: 0.07
Nodes (50): UserManager, build_authorize_url(), claims_from_tokens(), exchange_code_for_tokens(), _fetch_jwks(), fetch_oidc_metadata(), fetch_userinfo(), get_or_create_user_from_sso() (+42 more)

### Community 5 - "Layout.jsx"
Cohesion: 0.08
Nodes (27): OrganizationPage, ArrowUp(), Moon(), Sun(), InstallPrompt(), Layout(), OrgSwitcher(), PushNotificationPrompt() (+19 more)

### Community 6 - "forum/views.py"
Cohesion: 0.08
Nodes (42): DiscussionCommentAdmin, DiscussionTopicAdmin, ForumReportAdmin, register, Civic discussion boards and report reasons for the community forum., Only platform moderators skip pre-moderation so citizen posts stay in the queue., Editors, moderators, and org content leads can post expert replies., user_is_forum_expert() (+34 more)

### Community 7 - "queryKeys.js"
Cohesion: 0.11
Nodes (20): SsoCallbackPage, TutorPage, LanguageSwitcher(), mockRefreshUser, mockUpdateProfile, applyDirection(), initial, DEFAULT_LANGUAGE (+12 more)

### Community 8 - "conftest.py"
Cohesion: 0.08
Nodes (24): Command, BaseCommand, Role, create_organization_with_owner(), generate_unique_slug(), Create an organization and make ``owner`` its owner member., admin_user(), api_client() (+16 more)

### Community 9 - "Icons.jsx"
Cohesion: 0.20
Nodes (18): NotificationsPage, AcademicCap(), Bell(), BookOpen(), Calendar(), ChatBubble(), CloudArrowDown(), Eye() (+10 more)

### Community 10 - "bind_client_to_org"
Cohesion: 0.08
Nodes (9): bind_client_to_org(), Authenticate and scope requests to ``org`` (creates membership if needed)., TestArticles, django_db, TestOrgAnalytics, TestInAppBroadcast, TestQuizzes, TestCertificateTask (+1 more)

### Community 11 - "ui.jsx"
Cohesion: 0.11
Nodes (25): DashboardPage, ProfilePage, GamificationSummary(), EyeOff(), ORG_ROLE_STYLES, OrgRoleBadge(), passwordStrength(), PasswordStrengthBar() (+17 more)

### Community 12 - "AuthContext.jsx"
Cohesion: 0.13
Nodes (20): AdminPage, ProtectedRoute(), mockedUseAuth, mockUser, AuthContext, AuthProvider(), ADMIN, CITIZEN (+12 more)

### Community 13 - "log_activity"
Cohesion: 0.06
Nodes (36): ActivityLog, Meta, ActivityLogSerializer, Meta, _client_meta(), compute_integrity_hash(), log_activity(), Verify hash-chain integrity for recent activity logs. (+28 more)

### Community 14 - "core/middleware.py"
Cohesion: 0.08
Nodes (15): client_ip_from_request(), ip_allowed(), IP allowlist helpers and read-replica database router., Return True when allowlist is empty or client_ip matches an entry., Route reads to DATABASES['replica'] when configured., ReadReplicaRouter, ContentSecurityPolicyMiddleware, IpAllowlistMiddleware (+7 more)

### Community 15 - "event_views.py"
Cohesion: 0.06
Nodes (35): CivicEventAdmin, CivicNewsAdmin, EventSignupAdmin, PollAdmin, register, _all_day_dates(), _as_aware(), build_ics() (+27 more)

### Community 16 - "EventsDetailPage.jsx"
Cohesion: 0.11
Nodes (27): EventsDetailPage, EventsEditorPage, EventsManagePage, EventsPage, Breadcrumb(), EVENT_KINDS, EventKindBadge(), KIND_CLASS (+19 more)

### Community 17 - "articles.js"
Cohesion: 0.10
Nodes (27): App(), guard(), ErrorBoundary, OfflineBanner(), useOnlineStatus(), fetchOrCache(), listCacheKey(), loadArticle() (+19 more)

### Community 18 - "ArticleViewSet"
Cohesion: 0.16
Nodes (8): ArticleAttachmentUploadView, ArticleImageUploadView, ArticleViewSet, action, APIView, extend_schema, Upload a PDF or document attachment for an article (e.g. full constitution…, Upload an image for featured media or inline markdown embeds.

### Community 19 - "notifications/views.py"
Cohesion: 0.14
Nodes (17): BroadcastNotificationSerializer, WebPushSubscribeSerializer, WebPushSubscription, cleanup_push_subscriptions(), push_subscription_stats(), BroadcastNotificationView, Meta, NotificationListView (+9 more)

### Community 20 - "session.py"
Cohesion: 0.10
Nodes (17): JWTCookieAuthentication, Cookie-aware JWT authentication. Checks httpOnly cookies first (preferred, more…, Authenticate via httpOnly cookie if present; fall back to Bearer header., check_session_idle(), get_session_epoch(), is_privileged_user(), Server-side session controls: idle timeout and epoch-based revocation., Privileged sessions enforce idle timeout (platform staff or org admins). (+9 more)

### Community 21 - "ArticleEditorPage.jsx"
Cohesion: 0.19
Nodes (11): ArticleEditorPage, MediaPlayer(), renderMarkdown(), API_ORIGIN, resolveMediaUrl(), getEmbedInfo(), ArticleEditorPage(), EMPTY_FORM (+3 more)

### Community 22 - "media_views.py"
Cohesion: 0.13
Nodes (14): annotate_is_bookmarked(), Annotate ``is_bookmarked`` for article (``article_id``) or media (``media_id``)., _can_see_unpublished(), MediaAssetFilter, MediaAssetViewSet, MediaAudioUploadView, MediaVideoUploadView, Meta (+6 more)

### Community 23 - "learning/views.py"
Cohesion: 0.06
Nodes (25): api_view, CivicNewsViewSet, CivicNewsSerializer, CategorySerializer, Meta, ArticleFilter, _can_see_unpublished(), CategoryViewSet (+17 more)

### Community 24 - "ArticleSerializer"
Cohesion: 0.10
Nodes (5): ArticleSerializer, _can_publish_directly(), MediaAssetSerializer, validate_http_url(), TestMediaHttpUrlValidation

### Community 25 - "useAuth"
Cohesion: 0.09
Nodes (34): ArticlesManagePage, CertificatesPage, ForumPage, ResultsPage, SavedPage, SearchPage, BookmarkButton(), Bookmark() (+26 more)

### Community 26 - "tutor/views.py"
Cohesion: 0.13
Nodes (22): ChatRequestSerializer, ChatResponseSerializer, TutorMessageSerializer, TutorSessionSerializer, TutorSessionSummarySerializer, TutorSourceSerializer, TutorUsageSerializer, get_tutor_service() (+14 more)

### Community 27 - "apply_subscription_updated"
Cohesion: 0.19
Nodes (11): apply_checkout_completed(), _apply_plan_code(), apply_subscription_deleted(), apply_subscription_updated(), plan_code_for_stripe_price(), Sync subscription after Stripe Checkout completes., Sync plan/status when Stripe subscription changes., Downgrade to the free plan when a paid subscription ends. (+3 more)

### Community 28 - "dependencies"
Cohesion: 0.08
Nodes (25): axios, dompurify, dependencies, axios, dompurify, i18next, i18next-browser-languagedetector, idb (+17 more)

### Community 29 - "scim.py"
Cohesion: 0.16
Nodes (15): OrganizationScimToken, Bearer token for SCIM 2.0 provisioning integrations (hashed at rest)., authenticate_scim(), _group_to_scim(), APIView, SCIM 2.0 Groups — mapped to organization departments., ScimGroupDetailView, ScimGroupsView (+7 more)

### Community 30 - "tenants/models.py"
Cohesion: 0.05
Nodes (37): _event_at(), PlanAdmin, register, SubscriptionAdmin, Meta, Plan, A subscription tier with pricing and per-tenant quotas., Subscription (+29 more)

### Community 31 - "integrations.py"
Cohesion: 0.07
Nodes (39): build_integrations_report(), check_cache(), check_celery(), check_database(), check_email(), check_oidc(), check_pypdf(), check_sentry() (+31 more)

### Community 32 - "engagement/models.py"
Cohesion: 0.11
Nodes (15): Campaign, CivicNews, Meta, Poll, PollOption, Public civic information with an explicit claim-type label. Claim types are…, Citizen report of suspected misinformation. Not a republication of the rumour., SuspiciousContentReport (+7 more)

### Community 33 - "devDependencies"
Cohesion: 0.09
Nodes (23): autoprefixer, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, devDependencies, autoprefixer, @eslint/js, eslint-plugin-react-hooks (+15 more)

### Community 34 - "engagement/views.py"
Cohesion: 0.17
Nodes (10): PetitionSignature, PollVote, PollCreateSerializer, PollSerializer, PollVoteSerializer, atomic, PetitionSignView, PollListCreateView (+2 more)

### Community 35 - "sms_views.py"
Cohesion: 0.13
Nodes (18): register, SmsMessageAdmin, WebPushSubscriptionAdmin, SmsMessage, BroadcastSmsSerializer, Meta, SendSmsSerializer, SmsMessageSerializer (+10 more)

### Community 36 - "django_db"
Cohesion: 0.17
Nodes (5): django_db, TestEngagement, TestGamification, TestMediaCaptions, TestTutorStream

### Community 37 - "test_article_translation.py"
Cohesion: 0.07
Nodes (30): Command, BaseCommand, apply_article_translation(), _build_updates(), chunk_markdown(), detect_language(), _is_blank(), Automatic English/Arabic translation for civic-education articles. Detects the… (+22 more)

### Community 39 - "test_product_features.py"
Cohesion: 0.14
Nodes (7): django_db, TestAuditLogs, TestAvatarUpload, TestPhoneVerification, TestResendVerificationEmail, TestUnsuspendUser, TestWebPushSubscribe

### Community 40 - "QuizTakePage.jsx"
Cohesion: 0.20
Nodes (14): QuizTakePage, QuizzesPage, CardSkeleton(), contentLanguage(), localizedField(), localizedQuestion(), localizedQuestionOptions(), localizedQuiz() (+6 more)

### Community 41 - "Alert"
Cohesion: 0.16
Nodes (21): NewsDetailPage, CLAIM_ALERT, CLAIM_STYLES, claimAlertKind(), ClaimBadge(), ClaimLegend(), NEWS_CLAIM_TYPES, NEWS_TOPICS (+13 more)

### Community 42 - "Notification"
Cohesion: 0.14
Nodes (17): _get_or_create_prefs(), notify_user(), Unified notification fan-out. Call :func:`notify_user` to deliver a…, Create an in-app Notification and fan-out to configured channels. Returns the…, Fire-and-forget async send to the user's WebSocket group., _sms_push(), _web_push(), _ws_push() (+9 more)

### Community 43 - "accounts/models.py"
Cohesion: 0.11
Nodes (12): AbstractBaseUser, Optional, coarse profile fields for civic poll summaries. Values are states /…, EmailVerificationToken, Meta, User, UserProfile, ensure_profile(), receiver (+4 more)

### Community 44 - "TutorChat"
Cohesion: 0.13
Nodes (13): register, TutorChatAdmin, get_chat_session_history(), list_chat_sessions(), Read access to persisted tutor conversations., Return ordered messages for a persisted session owned by the user., Summarize recent tutor conversations persisted for the user., Meta (+5 more)

### Community 45 - "NotificationConsumer"
Cohesion: 0.14
Nodes (10): AsyncWebsocketConsumer, _group_name(), NotificationConsumer, WebSocket consumer for real-time in-app notifications. Each authenticated user…, Push a notification dict to all WebSocket connections for ``user_pk``. Call…, WebSocket endpoint: /ws/notifications/ Authenticate via: -…, Receive a notification event from the channel layer and forward it to the…, send_notification_to_user() (+2 more)

### Community 46 - "CivicUser"
Cohesion: 0.18
Nodes (5): CivicUser, HttpUser, task, Locust load test for the Civic Education RSS API. Simulates the read-heavy…, Register and log in a unique user, then cache the auth header.

### Community 47 - "Command"
Cohesion: 0.29
Nodes (4): Command, BaseCommand, Path, Disaster-recovery restore drill. Creates a logical backup of the current…

### Community 48 - "test_deploy.py"
Cohesion: 0.07
Nodes (27): CoreConfig, AppConfig, production_security_checks(), register, Validate settings required for a safe production deployment., Helpers for building Django ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS lists., Split comma-separated host strings and return de-duplicated hosts., Return the Render service hostname from platform-injected env vars. (+19 more)

### Community 49 - "tutor/services.py"
Cohesion: 0.14
Nodes (24): _daily_cache_key(), enforce_budget(), get_daily_limit(), get_daily_usage(), increment_daily_usage(), Daily message quota for the AI tutor. Usage is counted in Redis for speed and…, Return today's usage from Redis cache, seeding from DB on cold miss., Increment Redis counter and persist to DB asynchronously. (+16 more)

### Community 50 - "services.js"
Cohesion: 0.08
Nodes (30): AcceptInvitePage, BillingPage, ForgotPasswordPage, QuizzesManagePage, AuthShell(), FEATURES, EmailVerifyBanner(), PlatformLogo() (+22 more)

### Community 51 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, baseUrl, checkJs, jsx, module, moduleResolution, target, types (+4 more)

### Community 52 - "Pre-launch checklist"
Cohesion: 0.10
Nodes (20): 10. Ongoing operations, 11. Organization invites, 12. Error monitoring (Sentry), 13. Database backups, 14. E2E testing, 1. Domain and TLS, 2. Backend secrets, 3. Database (+12 more)

### Community 53 - "sms_providers.py"
Cohesion: 0.29
Nodes (6): AfricasTalkingSmsProvider, BaseSmsProvider, DummySmsProvider, get_sms_provider(), Log SMS in development; always succeeds., SmsSendResult

### Community 54 - "sms_services.py"
Cohesion: 0.24
Nodes (16): PhoneOTP, normalize_phone(), Normalize to E.164 for South Sudan (+211)., create_sms_log(), deliver_sms(), issue_phone_otp(), org_member_phones(), queue_sms_to_phone() (+8 more)

### Community 55 - "accounts/serializers.py"
Cohesion: 0.12
Nodes (10): Meta, PasswordResetConfirmSerializer, PasswordResetOtpConfirmSerializer, PasswordResetOtpRequestSerializer, PasswordResetRequestSerializer, RegisterSerializer, RoleSerializer, UserProfileSerializer (+2 more)

### Community 56 - "Command"
Cohesion: 0.11
Nodes (9): absolute_media_url(), build_topic_svg(), Command, BaseCommand, Prefer official PDF in seed_assets/ if present, else sample., Simple infographic card used as the lesson featured image., resolve_constitution_attachment(), django_db (+1 more)

### Community 57 - "test_tutor_providers.py"
Cohesion: 0.10
Nodes (17): _translation_provider(), _anthropic_configured(), AnthropicTutorProvider, BaseTutorProvider, get_tutor_provider(), _last_user_message(), _openai_configured(), Pluggable AI providers for the tutor. Mirrors ``apps/billing/providers.py``: a… (+9 more)

### Community 58 - "Production environment checklist — integrations"
Cohesion: 0.06
Nodes (35): 10. Compliance / monitoring gates (production), 1. Celery + Redis (required), 2. Stripe billing (required for paid SaaS), 2b. No Stripe / unsupported country (e.g. Uganda), 3. SMS — Africa's Talking (optional), 4. Web push — VAPID (optional), 5. AI tutor (optional), 6. Enterprise SSO — OpenID Connect (optional) (+27 more)

### Community 59 - "SuspiciousContentReportSerializer"
Cohesion: 0.18
Nodes (7): AwarenessOverviewView, _localize_title(), APIView, SuspiciousReportListCreateView, SuspiciousReportReviewView, SuspiciousContentReportReviewSerializer, SuspiciousContentReportSerializer

### Community 60 - "_parse_stats"
Cohesion: 0.29
Nodes (8): main(), _parse_stats(), Path, Headless Locust smoke gate for CI. Runs a short read-heavy scenario and fails…, Return fail_ratio, p95_ms, failures, requests from Locust CSV stats., Path, Unit tests for Locust CI gate stats parsing (no live Locust run)., test_parse_stats_aggregated()

### Community 61 - "Quiz"
Cohesion: 0.18
Nodes (12): Certificate, Meta, Question, Quiz, QuizAttempt, build_review_item(), grade_answer(), option_feedback_text() (+4 more)

### Community 62 - "TutorUnavailable"
Cohesion: 0.18
Nodes (6): APIException, TutorUnavailable, OpenAICompatibleTutorProvider, Any OpenAI-compatible endpoint: OpenAI, Ollama, OpenRouter, Groq, Together., FailingProvider, FailingProvider

### Community 63 - "Command"
Cohesion: 0.31
Nodes (4): Command, BaseCommand, Path, Create a PostgreSQL logical backup using pg_dump.

### Community 64 - "TestAuth"
Cohesion: 0.25
Nodes (3): django_db, TestAuth, TestHealthCheck

### Community 65 - "views/__init__.py"
Cohesion: 0.13
Nodes (30): AnonRateThrottle, EmailTokenObtainPairView, LoginView, LogoutView, APIView, Registration, login and logout., Account views. Split into cohesive submodules; every public view is re-exported…, ChangePasswordView (+22 more)

### Community 66 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, lint, preview, test, test:e2e, test:e2e:live (+1 more)

### Community 67 - "quizzes/serializers.py"
Cohesion: 0.24
Nodes (8): Meta, QuestionSerializer, QuestionWriteSerializer, QuizListSerializer, QuizSerializer, QuizWriteSerializer, Public catalog card — titles and counts, not question bodies., QuizViewSet

### Community 68 - "billing/services.py"
Cohesion: 0.18
Nodes (20): AnalyticsNotAvailable, count_usage(), ensure_subscription(), get_active_plan(), get_default_plan(), get_subscription(), invalidate_quota_cache(), plan_has_analytics() (+12 more)

### Community 69 - "TestNotifications"
Cohesion: 0.18
Nodes (4): notifications(), django_db, fixture, TestNotifications

### Community 70 - "helpers.js"
Cohesion: 0.19
Nodes (11): API, apiGlob(), LIVE_ADMIN_EMAIL, LIVE_ADMIN_PASSWORD, LIVE_API, LIVE_ORG_SLUG, liveAuthHeaders(), loginLive() (+3 more)

### Community 71 - "TestPlatformSupportAndSecurity"
Cohesion: 0.18
Nodes (4): django_db, TestContentPacks, TestOrgRoleRBAC, TestPlatformSupportAndSecurity

### Community 72 - "TestBilling"
Cohesion: 0.15
Nodes (5): django_db, TestBilling, TestMyOrganizations, TestOrganizationRegistration, TestQuotas

### Community 73 - "TestForum"
Cohesion: 0.13
Nodes (3): django_db, TestAnalytics, TestForum

### Community 74 - "TenantsConfig"
Cohesion: 0.33
Nodes (3): AppConfig, TenantsConfig, Tenant signal handlers. Subscription provisioning on organization creation…

### Community 75 - "TestArticleI18n"
Cohesion: 0.18
Nodes (4): django_db, TestArticleI18n, TestQuizI18n, TestQuizOptionsI18n

### Community 76 - "Load testing (Locust)"
Cohesion: 0.17
Nodes (12): Background tasks (Celery + Redis), CI load-test gate, CI load-test gate, Eager fallback (dev / test), Getting meaningful numbers, Headless ramp toward the SRS concurrency target, Institutional scale notes (10k concurrent), Load testing (Locust) (+4 more)

### Community 77 - "Backend setup"
Cohesion: 0.15
Nodes (13): AI tutor (RAG), API reference, Backend setup, Background tasks (Celery), Civic Education RSS, Default accounts (after `seed_data`), Deployment (Render), Load testing (+5 more)

### Community 78 - "AccessibilityContext.jsx"
Cohesion: 0.23
Nodes (15): AccessibilityMenu(), ReadAloudButton(), AccessibilityContext, AccessibilityProvider(), useAccessibility(), applyA11ySettings(), DEFAULT_A11Y, FONT_SCALES (+7 more)

### Community 79 - "get_current_organization"
Cohesion: 0.08
Nodes (22): _attempts_queryset(), _bucket_counts(), build_dashboard_summary(), build_institutional_report_pdf(), build_language_usage(), build_member_progress(), build_progress_csv(), build_regional_engagement() (+14 more)

### Community 81 - "package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 83 - "Civic Education RSS — Frontend"
Cohesion: 0.22
Nodes (8): Civic Education RSS — Frontend, Deployment, Environment variables, Features, Local setup, Project structure, Requirements, Scripts

### Community 86 - "enable_mfa"
Cohesion: 0.10
Nodes (14): enable_mfa(), login_user(), Enroll a test user in TOTP MFA (privileged routes require this)., Log in via API, completing MFA when enrolled., django_db, TestIpAllowlist, TestScimProvisioning, TestSessionControls (+6 more)

### Community 87 - "Article"
Cohesion: 0.05
Nodes (54): BookmarkViewSet, Saved-lesson list and delete., BookmarkError, Toggle and annotate saved lessons (bookmarks)., Raised when a bookmark cannot be created or removed., Save or unsave an article. Returns True when the article is now bookmarked., Save or unsave media. Returns True when the media is now bookmarked., _require_organization() (+46 more)

### Community 88 - "TestPasswordReset"
Cohesion: 0.13
Nodes (5): django_db, TestLogoutBlacklist, TestPasswordReset, TestSuspension, TestTokenRefresh

### Community 89 - "vercel.json"
Cohesion: 0.50
Nodes (3): buildCommand, outputDirectory, rewrites

### Community 96 - "Constitution & controlled documents"
Cohesion: 0.17
Nodes (12): 1. Add source files, 2. Run seed, 3. Verify, API path, Constitution & controlled documents, Option A — Seed data (recommended for demos), Option B — Article editor (production / org admins), Overview (+4 more)

### Community 97 - "django_db"
Cohesion: 0.40
Nodes (3): django_db, TestArticlePublishBroadcast, TestEmailTask

### Community 98 - "AI Tutor — RAG & PDF grounding"
Cohesion: 0.17
Nodes (12): AI Tutor — RAG & PDF grounding, API endpoints, Constitution & PDF content, Dependencies, Frontend, GET `/api/tutor/usage/platform/` — platform admin, How retrieval works, Limits & caching (+4 more)

### Community 142 - "Enterprise features (Government / NGO)"
Cohesion: 0.25
Nodes (8): Certification readiness, Content governance & reporting, Enterprise features (Government / NGO), Grade-A controls (summary), Identity provisioning, Org structure & scale, Production ops, Security & compliance

### Community 143 - "get_preferred_language"
Cohesion: 0.18
Nodes (4): get_preferred_language(), Resolve API content language to ``en`` or ``ar`` only., MediaAssetSummarySerializer, Compact nested representation for articles.

### Community 145 - "Compliance readiness (SOC 2 / ISO 27001)"
Cohesion: 0.33
Nodes (6): Compliance readiness (SOC 2 / ISO 27001), Control matrix, Evidence pack (in-product), Production security baseline (must be true before audit), Recurring ops (auditor will ask), What certification still requires (outside this repo)

### Community 146 - "Disaster recovery"
Cohesion: 0.33
Nodes (6): Automated backup, CI, Disaster recovery, Manual restore (true incident), Restore drill (required before audits), RPO / RTO targets (ops commitment)

### Community 148 - "bump_session_epoch"
Cohesion: 0.25
Nodes (6): bump_session_epoch(), Invalidate all outstanding JWTs for this user by advancing session_epoch., extend_schema, APIView, SCIM User resource: get / patch / deactivate., ScimUserDetailView

### Community 149 - "TestBookmarks"
Cohesion: 0.20
Nodes (3): django_db, TestBookmarks, TestPublicQuizList

### Community 150 - "TestTopicModeration"
Cohesion: 0.15
Nodes (5): django_db, TestCommentModeration, TestPendingQueue, TestTopicModeration, TestTopicVisibility

### Community 192 - "billing/views.py"
Cohesion: 0.21
Nodes (13): get_billing_provider(), CheckoutSerializer, Meta, PlanSerializer, SubscriptionSerializer, BillingPortalView, CheckoutView, CurrentSubscriptionView (+5 more)

### Community 196 - "engagement/serializers.py"
Cohesion: 0.17
Nodes (10): Petition, CampaignCreateSerializer, CampaignSerializer, Meta, PetitionCreateSerializer, PetitionSerializer, PollOptionSerializer, CampaignListCreateView (+2 more)

### Community 197 - "Membership"
Cohesion: 0.08
Nodes (44): check_quota(), Raise ``QuotaExceeded`` if creating one more ``resource`` would exceed the plan., Public platform branding strings., Department, Membership, Meta, OrganizationInvite, Pending email invitation to join an organization. (+36 more)

### Community 198 - "Civic Education RSS API Reference"
Cohesion: 0.29
Nodes (7): Civic Education RSS API Reference, Conventions, Endpoint index, Gamification & engagement, Ops commands, Related docs, Tutor API (summary)

### Community 199 - "gamification/services.py"
Cohesion: 0.15
Nodes (15): Badge, Meta, UserBadge, BadgeSerializer, EarnedBadgeSerializer, GamificationSummarySerializer, Meta, award_xp() (+7 more)

### Community 200 - "test_tutor_retrieval.py"
Cohesion: 0.05
Nodes (48): load_constitution_text(), enqueue_article_translation(), maintain_tutor_index(), notify_on_publish(), receiver, track_attachment_change(), build_tutor_index_text(), Build and maintain pre-indexed tutor search text on articles. (+40 more)

### Community 201 - "Testing & CI"
Cohesion: 0.20
Nodes (10): Backend tests, CI pipeline (`.github/workflows/ci.yml`), E2E tests (Playwright), Environment variables (live e2e), Frontend unit tests (Vitest), Live backend (`e2e-live` CI job), Mocked API (default — `frontend` CI job), Ops smoke (loadtest job) (+2 more)

### Community 202 - "TestSmsAlerts"
Cohesion: 0.25
Nodes (3): django_db, TestPhoneOtp, TestSmsAlerts

### Community 203 - "user_management.py"
Cohesion: 0.18
Nodes (14): assignable_roles_for(), is_platform_admin(), is_super_admin(), Platform role names and permission groups. Guest is unauthenticated (no Role…, role_name(), _get_managed_user(), APIView, extend_schema (+6 more)

### Community 204 - "TestUserSuspendIsolation"
Cohesion: 0.29
Nodes (3): django_db, TestUserList, TestUserSuspendIsolation

### Community 207 - "sso_views.py"
Cohesion: 0.24
Nodes (5): APIView, extend_schema, SsoCallbackView, SsoLoginView, SsoStatusView

### Community 210 - "BaseBillingProvider"
Cohesion: 0.12
Nodes (6): BaseBillingProvider, CheckoutResult, DummyBillingProvider, Pluggable billing providers. The ``dummy`` provider requires no external…, No-op provider for local dev/tests; activates plans instantly., StripeBillingProvider

### Community 211 - "TestTenantIsolation"
Cohesion: 0.25
Nodes (4): An article cannot reference a category that belongs to a different org., Org switcher: header selects another org the user belongs to., The tenant middleware must ignore X-Tenant-Slug for orgs the user doesn't…, TestTenantIsolation

### Community 217 - "RecordingProvider"
Cohesion: 0.29
Nodes (4): django_db, Honors the (text, 0) deltas then ('', total_tokens) terminal contract., RecordingProvider, TestServiceHonorsProviderContract

### Community 218 - "prompts.py"
Cohesion: 0.16
Nodes (13): normalize_language(), normalize_primary_color(), Shared application constants., Return ``en`` or ``ar``; any other value maps to ``en``., Return green default when ``color`` is a legacy blue brand value., curriculum_category_list(), Official civic curriculum catalog (15 learning modules). Seed data, the AI…, Human-readable list for tutor prompts. (+5 more)

### Community 221 - "profile.py"
Cohesion: 0.11
Nodes (10): ProfileUpdateSerializer, UserSerializer, AvatarUploadView, DeactivateAccountView, MyDataExportView, ProfileView, APIView, Self-service profile, avatar, data export and deactivation. (+2 more)

### Community 222 - "TestTutorChat"
Cohesion: 0.18
Nodes (3): django_db, TestTutorAdminUsage, TestTutorChat

### Community 223 - "upload_file"
Cohesion: 0.16
Nodes (15): build_handout_pdf(), One-page learner handout (key facts infographic + reminder)., extend_schema, get_signed_url(), get_supabase_client(), _local_media_url(), _save_local_file(), upload_bytesio() (+7 more)

### Community 225 - "TestCivicNews"
Cohesion: 0.31
Nodes (3): _make_news(), django_db, TestCivicNews

### Community 226 - "TestAwareness"
Cohesion: 0.25
Nodes (3): django_db, test_seed_includes_fact_or_fiction_and_awareness_articles(), TestAwareness

### Community 230 - "TestGlobalSearch"
Cohesion: 0.25
Nodes (3): django_db, TestGlobalSearch, TestTutorHistory

### Community 240 - "broadcast_notification_task"
Cohesion: 0.50
Nodes (3): broadcast_notification_task(), Fan out an in-app notification to active users in batches., TestBroadcastTask

### Community 241 - "test_org_analytics.py"
Cohesion: 0.60
Nodes (4): free_plan(), org_admin_member(), pro_plan(), fixture

### Community 247 - "CookieTokenRefreshView"
Cohesion: 0.22
Nodes (6): CookieAwareTokenRefreshSerializer, CookieTokenRefreshView, Cookie-aware JWT refresh — accepts refresh from body or httpOnly cookie., Refresh access tokens using body or the httpOnly refresh cookie., TokenRefreshSerializer, TokenRefreshView

### Community 251 - "TestPolls"
Cohesion: 0.36
Nodes (4): _open_poll(), django_db, TestPollOpinionAnalytics, TestPolls

### Community 253 - "create_default_subscription"
Cohesion: 0.67
Nodes (3): create_default_subscription(), receiver, Every new organization starts on the default (free) plan.

### Community 259 - "core/permissions.py"
Cohesion: 0.17
Nodes (14): check_mfa_enrolled(), Raise ``MfaSetupRequired`` when a privileged user has not enrolled MFA., IsAdmin, IsCitizenOrAbove, IsEditor, IsEditorOrAdmin, IsModerator, IsModeratorOrAdmin (+6 more)

### Community 264 - "App.jsx"
Cohesion: 0.06
Nodes (36): ArticleDetailPage, ArticlesPage, AwarenessPage, CategoriesManagePage, ContactPage, MediaDetailPage, MediaEditorPage, MediaManagePage (+28 more)

## Knowledge Gaps
- **297 isolated node(s):** `Migration`, `Migration`, `Migration`, `Migration`, `Migration` (+292 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **88 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `bind_client_to_org()` connect `bind_client_to_org` to `views/mfa.py`, `forum/views.py`, `conftest.py`, `TestLearningProgress`, `log_activity`, `TestMediaLibraryApi`, `event_views.py`, `TestBookmarks`, `TestTopicModeration`, `tenants/models.py`, `integrations.py`, `engagement/models.py`, `django_db`, `test_product_features.py`, `test_deploy.py`, `Quiz`, `Membership`, `TestPlatformSupportAndSecurity`, `TestForum`, `TestSmsAlerts`, `TestArticleI18n`, `TestUserSuspendIsolation`, `enable_mfa`, `Article`, `TestTutorChat`, `TestCivicNews`, `TestAwareness`, `TestGlobalSearch`, `test_org_analytics.py`, `TestPolls`, `TestOrganizationInvites`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `get_current_organization()` connect `get_current_organization` to `quizzes/views.py`, `analytics/views.py`, `log_activity`, `core/middleware.py`, `ArticleViewSet`, `notifications/views.py`, `media_views.py`, `learning/views.py`, `ArticleSerializer`, `tenants/models.py`, `engagement/views.py`, `sms_views.py`, `tutor/services.py`, `sms_services.py`, `SuspiciousContentReportSerializer`, `billing/views.py`, `engagement/serializers.py`, `Membership`, `gamification/services.py`, `user_management.py`, `Article`, `prompts.py`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `log_activity()` connect `log_activity` to `views/mfa.py`, `quizzes/views.py`, `analytics/views.py`, `forum/views.py`, `conftest.py`, `ArticleViewSet`, `bump_session_epoch`, `media_views.py`, `learning/views.py`, `scim.py`, `tenants/models.py`, `accounts/serializers.py`, `views/__init__.py`, `Membership`, `user_management.py`, `TestUserSuspendIsolation`, `sso_views.py`, `get_current_organization`, `Article`, `profile.py`, `PhoneVerifyConfirmSerializer`, `RegisterView`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `Membership` (e.g. with `TenantMiddleware` and `CanDeleteOrgContent`) actually correct?**
  _`Membership` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Migration`, `Migration`, `Migration` to the rest of the system?**
  _297 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `views/mfa.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08478513356562137 - nodes in this community are weakly interconnected._
- **Should `TopicDetailPage.jsx` be split into smaller, more focused modules?**
  _Cohesion score 0.08095238095238096 - nodes in this community are weakly interconnected._