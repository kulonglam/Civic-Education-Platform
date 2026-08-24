# Graph Report - Civic Education Platform  (2026-08-21)

## Corpus Check
- 425 files · ~168,878 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2659 nodes · 6091 edges · 240 communities (163 shown, 77 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 345 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b8de06a8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- accounts/views.py
- scim.py
- quizzes/models.py
- analytics/views.py
- sso.py
- ui.jsx
- forum/views.py
- auth.py
- QuizTakePage.jsx
- learning/views.py
- bind_client_to_org
- BillingPage.jsx
- App.jsx
- useAuth
- core/middleware.py
- Icons.jsx
- billing/views.py
- ArticleDetailPage.jsx
- test_grade_a_enterprise.py
- notifications/views.py
- Membership
- conftest.py
- TutorPage.jsx
- ArticleSerializer
- billing/services.py
- audit/services.py
- tutor/services.py
- test_saas.py
- dependencies
- TestGlobalSearch
- enterprise_views.py
- integrations.py
- TenantModel
- devDependencies
- BaseBillingProvider
- sms_views.py
- django_db
- Organization
- eslint
- fan_out.py
- sms_services.py
- test_quizzes_forum.py
- apply_subscription_updated
- Role
- services.js
- NotificationConsumer
- CivicUser
- Command
- test_deploy.py
- get_current_organization
- test_tutor_retrieval.py
- compilerOptions
- Pre-launch checklist
- create_organization_with_owner
- sms_providers.py
- mfa.py
- tenants/models.py
- get_membership
- Production environment checklist — integrations
- CiSmokeUser
- _parse_stats
- test_auth_flows.py
- get_preferred_language
- Command
- TestAuth
- log_activity
- scripts
- tenants/permissions.py
- TestOrganizationInvites
- TestNotifications
- helpers.js
- Command
- main.jsx
- Command
- TenantsConfig
- quizzes/views.py
- Load testing (Locust)
- Backend setup
- upload_file
- GlobalSearchView
- Subscription
- package.json
- AccountsConfig
- Civic Education RSS — Frontend
- LearningConfig
- 0003_migrate_primary_color_to_green.py
- accounts/serializers.py
- broadcast_notification_task
- TestTopicModeration
- vercel.json
- AnalyticsConfig
- AuditConfig
- ForumConfig
- NotificationsConfig
- QuizzesConfig
- TutorConfig
- Constitution & controlled documents
- test_org_analytics.py
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
- QuizEditorPage.jsx
- @testing-library/user-event
- Compliance readiness (SOC 2 / ISO 27001)
- Disaster recovery
- @vitejs/plugin-react
- core/permissions.py
- OrganizationSerializer
- log_security_event
- extend_schema
- _upload_media_file
- TestLearningProgress
- Civic Education RSS API Reference
- EmailTokenObtainPairSerializer
- TestSmsAlerts
- Testing & CI
- CookieTokenRefreshView
- test_enterprise_gaps.py
- OrganizationSsoConfig
- jwt.js
- test_media_articles.py
- Command
- 0009_learning_progress.py
- TestArticleI18n
- constants.py
- PasswordResetConfirmSerializer
- PasswordResetOtpConfirmSerializer
- tailwindcss
- @testing-library/jest-dom
- @testing-library/react
- WebPushSubscriptionAdmin
- QuizViewSet
- managers.py
- EngagementConfig
- GamificationConfig
- TestBackfillAuditOrgs
- django_db
- django_db
- UserManager
- RegisterView
- BillingConfig
- globals
- @playwright/test
- start.sh
- vite
- 0006_userprofile_xp_points.py
- engagement/migrations/0001_initial.py
- gamification/migrations/0001_initial.py
- 0010_article_tutor_index_text_mediaasset_captions_url.py

## God Nodes (most connected - your core abstractions)
1. `bind_client_to_org()` - 110 edges
2. `get_current_organization()` - 93 edges
3. `log_activity()` - 73 edges
4. `Membership` - 66 edges
5. `extractError()` - 53 edges
6. `useAuth()` - 39 edges
7. `Role` - 37 edges
8. `Article` - 36 edges
9. `Organization` - 35 edges
10. `TenantModel` - 31 edges

## Surprising Connections (you probably didn't know these)
- `Command` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/management/commands/seed_data.py → backend/apps/accounts/models.py
- `user_requires_mfa()` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/mfa.py → backend/apps/accounts/models.py
- `RegisterSerializer` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/serializers.py → backend/apps/accounts/models.py
- `RoleSerializer` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/serializers.py → backend/apps/accounts/models.py
- `UserRoleUpdateSerializer` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/serializers.py → backend/apps/accounts/models.py

## Import Cycles
- None detected.

## Communities (240 total, 77 thin omitted)

### Community 0 - "accounts/views.py"
Cohesion: 0.14
Nodes (18): EmailVerificationToken, UserRoleUpdateSerializer, UserSerializer, AvatarUploadView, DeactivateAccountView, _get_managed_user(), MyDataExportView, ProfileView (+10 more)

### Community 1 - "scim.py"
Cohesion: 0.07
Nodes (33): JWTCookieAuthentication, Cookie-aware JWT authentication. Checks httpOnly cookies first (preferred, more…, Authenticate via httpOnly cookie if present; fall back to Bearer header., bump_session_epoch(), check_session_idle(), get_session_epoch(), is_privileged_user(), Server-side session controls: idle timeout and epoch-based revocation. (+25 more)

### Community 2 - "quizzes/models.py"
Cohesion: 0.25
Nodes (8): Certificate, Meta, Question, Quiz, QuizAttempt, QuestionWriteSerializer, bilingual_article(), fixture

### Community 3 - "analytics/views.py"
Cohesion: 0.15
Nodes (21): IsOrgAnalyticsAdmin, BasePermission, Organization owner or admin (analytics plan checked in the view)., AnalyticsForumView, AnalyticsLearningView, AnalyticsOverviewView, AnalyticsQuizzesView, ExportProgressCSVView (+13 more)

### Community 4 - "sso.py"
Cohesion: 0.07
Nodes (47): build_authorize_url(), claims_from_tokens(), exchange_code_for_tokens(), _fetch_jwks(), fetch_oidc_metadata(), fetch_userinfo(), get_or_create_user_from_sso(), get_org_sso_config() (+39 more)

### Community 5 - "ui.jsx"
Cohesion: 0.10
Nodes (37): CertificatesPage, QuizzesPage, GamificationSummary(), Trophy(), Pagination(), Alert(), CardSkeleton(), ConfirmDialog() (+29 more)

### Community 6 - "forum/views.py"
Cohesion: 0.12
Nodes (19): DiscussionComment, DiscussionTopic, Meta, CommentCreateSerializer, DiscussionCommentSerializer, DiscussionTopicCreateSerializer, DiscussionTopicSerializer, Meta (+11 more)

### Community 7 - "auth.py"
Cohesion: 0.11
Nodes (15): AnonRateThrottle, PasswordResetOtpRequestSerializer, APIView, extend_schema, SsoCallbackView, SsoLoginView, SsoStatusView, ChangePasswordView (+7 more)

### Community 8 - "QuizTakePage.jsx"
Cohesion: 0.18
Nodes (16): QuizTakePage, OfflineBanner(), useOnlineStatus(), api, getDb(), flushQuizQueue(), getQueuedQuizCount(), loadQuiz() (+8 more)

### Community 9 - "learning/views.py"
Cohesion: 0.08
Nodes (19): api_view, CategorySerializer, ArticleAttachmentUploadView, ArticleFilter, ArticleImageUploadView, ArticleViewSet, _can_see_unpublished(), CategoryViewSet (+11 more)

### Community 10 - "bind_client_to_org"
Cohesion: 0.08
Nodes (11): bind_client_to_org(), Authenticate and scope requests to ``org`` (creates membership if needed)., TestArticles, TestMediaLibraryApi, TestInAppBroadcast, TestCertificateTask, django_db, TestTutorAdminUsage (+3 more)

### Community 11 - "BillingPage.jsx"
Cohesion: 0.09
Nodes (21): BillingPage, AuthShell(), FEATURES, PlatformLogo(), UsageBar(), PLATFORM_LOGO_ALT, PLATFORM_LOGO_URL, PLATFORM_NAME (+13 more)

### Community 12 - "App.jsx"
Cohesion: 0.09
Nodes (17): ArticleDetailPage, ArticlesManagePage, ArticlesPage, ContactPage, DashboardPage, ForumPage, MediaDetailPage, MediaManagePage (+9 more)

### Community 13 - "useAuth"
Cohesion: 0.05
Nodes (49): AcceptInvitePage, AdminPage, OrganizationPage, SsoCallbackPage, ArrowUp(), Moon(), Sun(), InstallPrompt() (+41 more)

### Community 14 - "core/middleware.py"
Cohesion: 0.08
Nodes (15): client_ip_from_request(), ip_allowed(), IP allowlist helpers and read-replica database router., Return True when allowlist is empty or client_ip matches an entry., Route reads to DATABASES['replica'] when configured., ReadReplicaRouter, ContentSecurityPolicyMiddleware, IpAllowlistMiddleware (+7 more)

### Community 15 - "Icons.jsx"
Cohesion: 0.16
Nodes (18): NotificationsPage, Breadcrumb(), AcademicCap(), Bell(), BookOpen(), ChatBubble(), ChevronRight(), CloudArrowDown() (+10 more)

### Community 16 - "billing/views.py"
Cohesion: 0.32
Nodes (9): CheckoutSerializer, Meta, PlanSerializer, SubscriptionSerializer, BillingPortalView, CheckoutView, CurrentSubscriptionView, PlanListView (+1 more)

### Community 17 - "ArticleDetailPage.jsx"
Cohesion: 0.11
Nodes (28): ArticleEditorPage, MediaPlayer(), useDebouncedValue(), readingTime(), plainTextExcerpt(), renderMarkdown(), SANITIZE_OPTIONS, API_ORIGIN (+20 more)

### Community 18 - "test_grade_a_enterprise.py"
Cohesion: 0.16
Nodes (10): login_user(), Log in via API, completing MFA when enrolled., django_db, Grade-A enterprise: sessions, SCIM, compliance, support, IP allowlist., TestAuditIntegrity, TestIpAllowlist, TestScimProvisioning, TestSessionControls (+2 more)

### Community 19 - "notifications/views.py"
Cohesion: 0.11
Nodes (23): BroadcastNotificationSerializer, WebPushSubscribeSerializer, Notification, WebPushSubscription, cleanup_push_subscriptions(), push_subscription_stats(), notify_all_users(), notify_user() (+15 more)

### Community 20 - "Membership"
Cohesion: 0.11
Nodes (28): Membership, OrganizationInvite, Pending email invitation to join an organization., BulkImportRowSerializer, DepartmentSerializer, InvitePreviewSerializer, MemberInviteSerializer, MemberRoleUpdateSerializer (+20 more)

### Community 21 - "conftest.py"
Cohesion: 0.14
Nodes (16): admin_user(), api_client(), category(), citizen_user(), editor_user(), enable_mfa(), moderator_user(), org() (+8 more)

### Community 22 - "TutorPage.jsx"
Cohesion: 0.14
Nodes (22): TutorPage, LanguageSwitcher(), applyDirection(), initial, DEFAULT_LANGUAGE, normalizeLanguage(), RTL_LANGUAGES, sanitizeStoredLanguage() (+14 more)

### Community 23 - "ArticleSerializer"
Cohesion: 0.09
Nodes (9): ArticleSerializer, _can_publish_directly(), MediaAssetSerializer, MediaAssetSummarySerializer, Meta, Compact nested representation for articles., validate_http_url(), django_db (+1 more)

### Community 24 - "billing/services.py"
Cohesion: 0.17
Nodes (21): AnalyticsNotAvailable, check_quota(), count_usage(), ensure_subscription(), get_active_plan(), get_default_plan(), get_subscription(), invalidate_quota_cache() (+13 more)

### Community 25 - "audit/services.py"
Cohesion: 0.13
Nodes (10): Command, BaseCommand, ActivityLog, Meta, ActivityLogSerializer, Meta, ActivityLogExportView, ActivityLogListView (+2 more)

### Community 26 - "tutor/services.py"
Cohesion: 0.05
Nodes (58): register, TutorChatAdmin, Meta, DB-backed per-user daily message counter. Redis is used as a fast write-through…, TutorChat, TutorDailyUsage, Deduplicate retrieved chunks into citation cards for the API response., serialize_sources() (+50 more)

### Community 27 - "test_saas.py"
Cohesion: 0.18
Nodes (5): django_db, TestBilling, TestMyOrganizations, TestOrganizationRegistration, TestQuotas

### Community 28 - "dependencies"
Cohesion: 0.08
Nodes (25): axios, dompurify, dependencies, axios, dompurify, i18next, i18next-browser-languagedetector, idb (+17 more)

### Community 29 - "TestGlobalSearch"
Cohesion: 0.25
Nodes (3): django_db, TestGlobalSearch, TestTutorHistory

### Community 30 - "enterprise_views.py"
Cohesion: 0.11
Nodes (16): BulkMemberImportView, DepartmentDetailView, _org_support_snapshot(), OrganizationSsoConfigView, PlatformOrganizationDetailView, PlatformOrganizationListView, PlatformUsageSummaryView, APIView (+8 more)

### Community 31 - "integrations.py"
Cohesion: 0.08
Nodes (36): build_integrations_report(), check_anthropic(), check_cache(), check_celery(), check_database(), check_email(), check_oidc(), check_pypdf() (+28 more)

### Community 32 - "TenantModel"
Cohesion: 0.06
Nodes (45): Campaign, Meta, Petition, PetitionSignature, Poll, PollOption, PollVote, CampaignCreateSerializer (+37 more)

### Community 33 - "devDependencies"
Cohesion: 0.09
Nodes (23): autoprefixer, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, devDependencies, autoprefixer, @eslint/js, eslint-plugin-react-hooks (+15 more)

### Community 34 - "BaseBillingProvider"
Cohesion: 0.11
Nodes (8): BaseBillingProvider, CheckoutResult, DummyBillingProvider, get_billing_provider(), Pluggable billing providers. The ``dummy`` provider requires no external…, No-op provider for local dev/tests; activates plans instantly., StripeBillingProvider, extend_schema

### Community 35 - "sms_views.py"
Cohesion: 0.13
Nodes (18): DetailSerializer, MessageSerializer, Generic ``{"detail": "..."}`` response body., Generic ``{"message": "..."}`` response body., BroadcastSmsSerializer, Meta, SendSmsSerializer, SmsMessageSerializer (+10 more)

### Community 36 - "django_db"
Cohesion: 0.17
Nodes (5): django_db, TestEngagement, TestGamification, TestMediaCaptions, TestTutorStream

### Community 37 - "Organization"
Cohesion: 0.10
Nodes (22): shared_task, Send an email asynchronously with retry and logging. Replaces fail_silently so…, send_email_task(), MembershipAdmin, OrganizationAdmin, OrganizationInviteAdmin, register, Department (+14 more)

### Community 39 - "fan_out.py"
Cohesion: 0.15
Nodes (15): Push a notification dict to all WebSocket connections for ``user_pk``. Call…, send_notification_to_user(), _get_or_create_prefs(), notify_user(), Unified notification fan-out. Call :func:`notify_user` to deliver a…, Create an in-app Notification and fan-out to configured channels. Returns the…, Fire-and-forget async send to the user's WebSocket group., _sms_push() (+7 more)

### Community 40 - "sms_services.py"
Cohesion: 0.27
Nodes (16): PhoneOTP, SmsMessage, normalize_phone(), Normalize to E.164 for South Sudan (+211)., create_sms_log(), deliver_sms(), issue_phone_otp(), org_member_phones() (+8 more)

### Community 41 - "test_quizzes_forum.py"
Cohesion: 0.22
Nodes (4): django_db, TestAnalytics, TestForum, TestQuizzes

### Community 42 - "apply_subscription_updated"
Cohesion: 0.16
Nodes (13): apply_checkout_completed(), _apply_plan_code(), apply_subscription_deleted(), apply_subscription_updated(), plan_code_for_stripe_price(), Sync subscription after Stripe Checkout completes., Sync plan/status when Stripe subscription changes., Downgrade to the free plan when a paid subscription ends. (+5 more)

### Community 43 - "Role"
Cohesion: 0.12
Nodes (12): AbstractBaseUser, Command, BaseCommand, Meta, Role, User, UserProfile, ensure_profile() (+4 more)

### Community 44 - "services.js"
Cohesion: 0.08
Nodes (26): CategoriesManagePage, EngagementPage, ForgotPasswordPage, MediaEditorPage, ResetPasswordPage, TopicDetailPage, EmailVerifyBanner(), ChevronLeft() (+18 more)

### Community 45 - "NotificationConsumer"
Cohesion: 0.15
Nodes (8): AsyncWebsocketConsumer, _group_name(), NotificationConsumer, WebSocket consumer for real-time in-app notifications. Each authenticated user…, WebSocket endpoint: /ws/notifications/ Authenticate via: -…, Receive a notification event from the channel layer and forward it to the…, ASGI config for Civic Education RSS. Handles both HTTP (via Django WSGI-over-…, database_sync_to_async

### Community 46 - "CivicUser"
Cohesion: 0.18
Nodes (5): CivicUser, HttpUser, task, Locust load test for the Civic Education RSS API. Simulates the read-heavy…, Register and log in a unique user, then cache the auth header.

### Community 47 - "Command"
Cohesion: 0.29
Nodes (4): Command, BaseCommand, Path, Disaster-recovery restore drill. Creates a logical backup of the current…

### Community 48 - "test_deploy.py"
Cohesion: 0.07
Nodes (27): CoreConfig, AppConfig, production_security_checks(), register, Validate settings required for a safe production deployment., Helpers for building Django ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS lists., Split comma-separated host strings and return de-duplicated hosts., Return the Render service hostname from platform-injected env vars. (+19 more)

### Community 49 - "get_current_organization"
Cohesion: 0.16
Nodes (15): _attempts_queryset(), build_dashboard_summary(), build_institutional_report_pdf(), build_member_progress(), build_my_learning_summary(), build_progress_csv(), org_member_users(), _parse_date() (+7 more)

### Community 50 - "test_tutor_retrieval.py"
Cohesion: 0.06
Nodes (46): maintain_tutor_index(), notify_on_publish(), receiver, track_attachment_change(), build_tutor_index_text(), Build and maintain pre-indexed tutor search text on articles., Combine article body and PDF attachment text for tutor retrieval., clear_current_organization() (+38 more)

### Community 51 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, baseUrl, checkJs, jsx, module, moduleResolution, target, types (+4 more)

### Community 52 - "Pre-launch checklist"
Cohesion: 0.10
Nodes (20): 10. Ongoing operations, 11. Organization invites, 12. Error monitoring (Sentry), 13. Database backups, 14. E2E testing, 1. Domain and TLS, 2. Backend secrets, 3. Database (+12 more)

### Community 53 - "create_organization_with_owner"
Cohesion: 0.12
Nodes (12): create_organization_with_owner(), Create an organization and make ``owner`` its owner member., django_db, TestAuditLogTenantScope, public_org(), fixture, django_db, TestDemoteLegacyOrgAdmins (+4 more)

### Community 54 - "sms_providers.py"
Cohesion: 0.29
Nodes (6): AfricasTalkingSmsProvider, BaseSmsProvider, DummySmsProvider, get_sms_provider(), Log SMS in development; always succeeds., SmsSendResult

### Community 55 - "mfa.py"
Cohesion: 0.14
Nodes (14): generate_totp_secret(), issue_mfa_challenge(), provisioning_uri(), TOTP multi-factor authentication for privileged accounts., Platform admins and organization owners/admins must use MFA when org requires…, totp_for_secret(), user_has_mfa_enabled(), user_requires_mfa() (+6 more)

### Community 56 - "tenants/models.py"
Cohesion: 0.10
Nodes (25): MediaAssetFilter, Meta, Media library API: CRUD + audio/video uploads., Article, ArticleProgress, Category, MediaAsset, MediaProgress (+17 more)

### Community 57 - "get_membership"
Cohesion: 0.18
Nodes (5): check_mfa_enrolled(), Raise ``MfaSetupRequired`` when a privileged user has not enrolled MFA., _can_see_unpublished(), get_membership(), _platform_role_name()

### Community 58 - "Production environment checklist — integrations"
Cohesion: 0.06
Nodes (34): 10. Compliance / monitoring gates (production), 1. Celery + Redis (required), 2. Stripe billing (required for paid SaaS), 2b. No Stripe / unsupported country (e.g. Uganda), 3. SMS — Africa's Talking (optional), 4. Web push — VAPID (optional), 5. AI tutor — Anthropic (optional), 6. Enterprise SSO — OpenID Connect (optional) (+26 more)

### Community 59 - "CiSmokeUser"
Cohesion: 0.22
Nodes (4): CiSmokeUser, HttpUser, task, Lightweight Locust scenario for CI — avoids mass registration throttling.

### Community 60 - "_parse_stats"
Cohesion: 0.29
Nodes (8): main(), _parse_stats(), Path, Headless Locust smoke gate for CI. Runs a short read-heavy scenario and fails…, Return fail_ratio, p95_ms, failures, requests from Locust CSV stats., Path, Unit tests for Locust CI gate stats parsing (no live Locust run)., test_parse_stats_aggregated()

### Community 61 - "test_auth_flows.py"
Cohesion: 0.12
Nodes (6): django_db, TestEmailVerification, TestLogoutBlacklist, TestPasswordReset, TestSuspension, TestTokenRefresh

### Community 62 - "get_preferred_language"
Cohesion: 0.19
Nodes (5): get_preferred_language(), Resolve API content language to ``en`` or ``ar`` only., Meta, QuestionSerializer, QuizSerializer

### Community 63 - "Command"
Cohesion: 0.31
Nodes (4): Command, BaseCommand, Path, Create a PostgreSQL logical backup using pg_dump.

### Community 64 - "TestAuth"
Cohesion: 0.25
Nodes (3): django_db, TestAuth, TestHealthCheck

### Community 65 - "log_activity"
Cohesion: 0.08
Nodes (22): _client_meta(), compute_integrity_hash(), log_activity(), Verify hash-chain integrity for recent activity logs., verify_audit_chain(), MediaAssetViewSet, AuditIntegrityVerifyView, ComplianceEvidencePackView (+14 more)

### Community 66 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, lint, preview, test, test:e2e, test:e2e:live (+1 more)

### Community 67 - "tenants/permissions.py"
Cohesion: 0.23
Nodes (9): CanDeleteOrgContent, IsOrgContentEditor, IsOrgForumModerator, IsOrgMember, IsOrgOwnerOrAdmin, BasePermission, Articles/quizzes: platform editor/admin OR org owner/admin/content_manager., Forum moderation: platform moderator/admin OR org owner/admin/moderator. (+1 more)

### Community 69 - "TestNotifications"
Cohesion: 0.18
Nodes (4): notifications(), django_db, fixture, TestNotifications

### Community 70 - "helpers.js"
Cohesion: 0.19
Nodes (11): API, apiGlob(), LIVE_ADMIN_EMAIL, LIVE_ADMIN_PASSWORD, LIVE_API, LIVE_ORG_SLUG, liveAuthHeaders(), loginLive() (+3 more)

### Community 71 - "Command"
Cohesion: 0.14
Nodes (8): absolute_media_url(), Command, load_constitution_text(), BaseCommand, Prefer official PDF in seed_assets/ if present, else sample., resolve_constitution_attachment(), django_db, TestSeedDataContent

### Community 72 - "main.jsx"
Cohesion: 0.19
Nodes (6): App(), guard(), ErrorBoundary, queryClient, captureUiError(), initSentry()

### Community 73 - "Command"
Cohesion: 0.33
Nodes (3): Command, BaseCommand, Management command: report English/Arabic bilingual content completeness.…

### Community 74 - "TenantsConfig"
Cohesion: 0.33
Nodes (3): AppConfig, TenantsConfig, Tenant signal handlers. Subscription provisioning on organization creation…

### Community 75 - "quizzes/views.py"
Cohesion: 0.26
Nodes (10): CertificateSerializer, QuizAttemptSerializer, QuizAttemptSubmitSerializer, generate_certificate_number(), CertificateDownloadView, CertificateListView, APIView, extend_schema (+2 more)

### Community 76 - "Load testing (Locust)"
Cohesion: 0.17
Nodes (12): Background tasks (Celery + Redis), CI load-test gate, CI load-test gate, Eager fallback (dev / test), Getting meaningful numbers, Headless ramp toward the SRS concurrency target, Institutional scale notes (10k concurrent), Load testing (Locust) (+4 more)

### Community 77 - "Backend setup"
Cohesion: 0.15
Nodes (13): AI tutor (RAG), API reference, Backend setup, Background tasks (Celery), Civic Education RSS, Default accounts (after `seed_data`), Deployment (Render), Load testing (+5 more)

### Community 78 - "upload_file"
Cohesion: 0.23
Nodes (11): get_signed_url(), get_supabase_client(), _local_media_url(), _save_local_file(), upload_bytesio(), upload_file(), generate_certificate_pdf(), generate_certificate_pdf_task() (+3 more)

### Community 79 - "GlobalSearchView"
Cohesion: 0.40
Nodes (3): GlobalSearchView, APIView, extend_schema

### Community 80 - "Subscription"
Cohesion: 0.12
Nodes (15): PlanAdmin, register, SubscriptionAdmin, Meta, Plan, A subscription tier with pricing and per-tenant quotas., Subscription, create_default_subscription() (+7 more)

### Community 81 - "package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 83 - "Civic Education RSS — Frontend"
Cohesion: 0.22
Nodes (8): Civic Education RSS — Frontend, Deployment, Environment variables, Features, Local setup, Project structure, Requirements, Scripts

### Community 86 - "accounts/serializers.py"
Cohesion: 0.21
Nodes (7): Meta, PasswordResetRequestSerializer, ProfileUpdateSerializer, RegisterSerializer, RoleSerializer, UserProfileSerializer, PasswordResetRequestView

### Community 87 - "broadcast_notification_task"
Cohesion: 0.50
Nodes (3): broadcast_notification_task(), Fan out an in-app notification to active users in batches., TestBroadcastTask

### Community 88 - "TestTopicModeration"
Cohesion: 0.15
Nodes (5): django_db, TestCommentModeration, TestPendingQueue, TestTopicModeration, TestTopicVisibility

### Community 89 - "vercel.json"
Cohesion: 0.50
Nodes (3): buildCommand, outputDirectory, rewrites

### Community 96 - "Constitution & controlled documents"
Cohesion: 0.17
Nodes (12): 1. Add source files, 2. Run seed, 3. Verify, API path, Constitution & controlled documents, Option A — Seed data (recommended for demos), Option B — Article editor (production / org admins), Overview (+4 more)

### Community 97 - "test_org_analytics.py"
Cohesion: 0.18
Nodes (6): free_plan(), org_admin_member(), pro_plan(), django_db, fixture, TestOrgAnalytics

### Community 98 - "AI Tutor — RAG & PDF grounding"
Cohesion: 0.17
Nodes (12): AI Tutor — RAG & PDF grounding, API endpoints, Constitution & PDF content, Dependencies, Frontend, GET `/api/tutor/usage/platform/` — platform admin, How retrieval works, Limits & caching (+4 more)

### Community 142 - "Enterprise features (Government / NGO)"
Cohesion: 0.25
Nodes (8): Certification readiness, Content governance & reporting, Enterprise features (Government / NGO), Grade-A controls (summary), Identity provisioning, Org structure & scale, Production ops, Security & compliance

### Community 143 - "QuizEditorPage.jsx"
Cohesion: 0.50
Nodes (7): QuizEditorPage, buildPayload(), emptyQuestion(), optionsArMismatch(), optionsFromText(), questionFromApi(), QuizEditorPage()

### Community 145 - "Compliance readiness (SOC 2 / ISO 27001)"
Cohesion: 0.33
Nodes (6): Compliance readiness (SOC 2 / ISO 27001), Control matrix, Evidence pack (in-product), Production security baseline (must be true before audit), Recurring ops (auditor will ask), What certification still requires (outside this repo)

### Community 146 - "Disaster recovery"
Cohesion: 0.33
Nodes (6): Automated backup, CI, Disaster recovery, Manual restore (true incident), Restore drill (required before audits), RPO / RTO targets (ops commitment)

### Community 148 - "core/permissions.py"
Cohesion: 0.27
Nodes (10): IsAdmin, IsCitizenOrAbove, IsEditor, IsEditorOrAdmin, IsModerator, IsModeratorOrAdmin, IsOwnerOrAdmin, BasePermission (+2 more)

### Community 149 - "OrganizationSerializer"
Cohesion: 0.24
Nodes (6): normalize_primary_color(), Return green default when ``color`` is a legacy blue brand value., OrganizationSerializer, CurrentOrganizationView, OrganizationBySlugView, Public branding lookup for login pages and tenant-specific entry.

### Community 150 - "log_security_event"
Cohesion: 0.24
Nodes (9): custom_exception_handler(), MfaSetupRequired, APIException, Log permission denials and MFA setup blocks as security events., _client_ip(), log_security_event(), Any, Structured security event logging for monitoring and incident response. (+1 more)

### Community 192 - "extend_schema"
Cohesion: 0.22
Nodes (4): PhoneVerifyConfirmSerializer, LogoutView, PhoneVerifyConfirmView, extend_schema

### Community 196 - "_upload_media_file"
Cohesion: 0.27
Nodes (6): MediaAudioUploadView, MediaVideoUploadView, action, APIView, extend_schema, _upload_media_file()

### Community 198 - "Civic Education RSS API Reference"
Cohesion: 0.29
Nodes (7): Civic Education RSS API Reference, Conventions, Endpoint index, Gamification & engagement, Ops commands, Related docs, Tutor API (summary)

### Community 199 - "EmailTokenObtainPairSerializer"
Cohesion: 0.28
Nodes (7): consume_mfa_challenge(), issue_jwt_tokens(), EmailTokenObtainPairSerializer, MfaVerifyLoginView, Complete login after password verification with a TOTP code., Complete login after password verification when MFA is enabled., TokenObtainPairSerializer

### Community 200 - "TestSmsAlerts"
Cohesion: 0.25
Nodes (3): django_db, TestPhoneOtp, TestSmsAlerts

### Community 201 - "Testing & CI"
Cohesion: 0.20
Nodes (10): Backend tests, CI pipeline (`.github/workflows/ci.yml`), E2E tests (Playwright), Environment variables (live e2e), Frontend unit tests (Vitest), Live backend (`e2e-live` CI job), Mocked API (default — `frontend` CI job), Ops smoke (loadtest job) (+2 more)

### Community 202 - "CookieTokenRefreshView"
Cohesion: 0.22
Nodes (6): CookieAwareTokenRefreshSerializer, CookieTokenRefreshView, Cookie-aware JWT refresh — accepts refresh from body or httpOnly cookie., Refresh access tokens using body or the httpOnly refresh cookie., TokenRefreshSerializer, TokenRefreshView

### Community 203 - "test_enterprise_gaps.py"
Cohesion: 0.14
Nodes (8): Meta, Persisted security events for platform-admin monitoring dashboards., SecurityEvent, django_db, Tests for remaining enterprise gaps: org RBAC, content packs, platform support., TestContentPacks, TestOrgRoleRBAC, TestPlatformSupportAndSecurity

### Community 204 - "OrganizationSsoConfig"
Cohesion: 0.25
Nodes (5): Meta, OrganizationSsoConfig, Tenant-raised support case visible to platform operators., Per-organization OpenID Connect settings (Enterprise plan)., SupportCase

### Community 206 - "test_media_articles.py"
Cohesion: 0.43
Nodes (6): django_db, Coverage-oriented tests for media–article linking and MediaAsset helpers., test_article_can_attach_audio_and_video(), test_article_rejects_wrong_media_type(), test_media_asset_playback_url_external(), test_media_asset_playback_url_prefers_upload()

### Community 209 - "TestArticleI18n"
Cohesion: 0.18
Nodes (4): django_db, TestArticleI18n, TestQuizI18n, TestQuizOptionsI18n

### Community 210 - "constants.py"
Cohesion: 0.40
Nodes (4): normalize_language(), Shared application constants., Return ``en`` or ``ar``; any other value maps to ``en``., _user_language()

### Community 216 - "WebPushSubscriptionAdmin"
Cohesion: 0.40
Nodes (4): register, SmsMessageAdmin, WebPushSubscriptionAdmin, display

### Community 218 - "managers.py"
Cohesion: 0.50
Nodes (3): Manager that automatically scopes queries to the current organization. When a…, TenantManager, TenantQuerySet

### Community 222 - "django_db"
Cohesion: 0.40
Nodes (3): django_db, TestArticlePublishBroadcast, TestEmailTask

### Community 223 - "django_db"
Cohesion: 0.13
Nodes (6): django_db, TestAuditLogs, TestPhoneVerification, TestResendVerificationEmail, TestUnsuspendUser, TestWebPushSubscribe

## Knowledge Gaps
- **266 isolated node(s):** `Migration`, `Migration`, `Migration`, `Migration`, `Migration` (+261 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **77 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_current_organization()` connect `get_current_organization` to `accounts/views.py`, `analytics/views.py`, `learning/views.py`, `core/middleware.py`, `billing/views.py`, `notifications/views.py`, `Membership`, `OrganizationSerializer`, `ArticleSerializer`, `audit/services.py`, `tutor/services.py`, `enterprise_views.py`, `TenantModel`, `BaseBillingProvider`, `sms_views.py`, `sms_services.py`, `test_tutor_retrieval.py`, `tenants/models.py`, `get_membership`, `log_activity`, `tenants/permissions.py`, `_upload_media_file`, `quizzes/views.py`, `managers.py`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `Membership` connect `Membership` to `accounts/views.py`, `scim.py`, `sso.py`, `forum/views.py`, `learning/views.py`, `bind_client_to_org`, `test_grade_a_enterprise.py`, `notifications/views.py`, `conftest.py`, `audit/services.py`, `test_saas.py`, `enterprise_views.py`, `TenantModel`, `Organization`, `sms_services.py`, `Role`, `get_current_organization`, `test_tutor_retrieval.py`, `create_organization_with_owner`, `mfa.py`, `tenants/models.py`, `get_membership`, `tenants/permissions.py`, `quizzes/views.py`, `OrganizationSsoConfig`, `test_enterprise_gaps.py`, `test_media_articles.py`, `Subscription`, `test_org_analytics.py`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `bind_client_to_org()` connect `bind_client_to_org` to `quizzes/models.py`, `forum/views.py`, `test_grade_a_enterprise.py`, `notifications/views.py`, `Membership`, `conftest.py`, `audit/services.py`, `TestGlobalSearch`, `integrations.py`, `TenantModel`, `django_db`, `test_quizzes_forum.py`, `test_deploy.py`, `create_organization_with_owner`, `mfa.py`, `tenants/models.py`, `TestOrganizationInvites`, `TestLearningProgress`, `TestSmsAlerts`, `test_enterprise_gaps.py`, `test_media_articles.py`, `Subscription`, `TestArticleI18n`, `TestTopicModeration`, `django_db`, `test_org_analytics.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `Membership` (e.g. with `TenantMiddleware` and `CanDeleteOrgContent`) actually correct?**
  _`Membership` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Migration`, `Migration`, `Migration` to the rest of the system?**
  _266 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `accounts/views.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._
- **Should `scim.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07138047138047138 - nodes in this community are weakly interconnected._