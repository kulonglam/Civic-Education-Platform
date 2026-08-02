# Graph Report - Civic Education Platform  (2026-08-02)

## Corpus Check
- 423 files · ~167,859 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2546 nodes · 6620 edges · 241 communities (141 shown, 100 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 1145 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ad9a4c02`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- accounts/views.py
- log_activity
- quizzes/views.py
- get_current_organization
- sso.py
- ui.jsx
- forum/views.py
- Membership
- ProfilePage.jsx
- OrganizationInvite
- bind_client_to_org
- BillingPage.jsx
- App.jsx
- useAuth
- core/middleware.py
- extractError
- Subscription
- ArticleDetailPage.jsx
- Organization
- notifications/views.py
- enterprise_views.py
- conftest.py
- Icons.jsx
- SmsMessage
- billing/services.py
- Notification
- tutor/services.py
- test_saas.py
- dependencies
- Article
- grade_a_views.py
- SecurityEvent
- localizedContent.js
- devDependencies
- BaseBillingProvider
- sms_views.py
- MediaAssetSerializer
- learning/views.py
- tutor/views.py
- fan_out.py
- session.py
- Command
- apply_subscription_updated
- services.js
- NotificationConsumer
- CivicUser
- Command
- test_deploy.py
- core/permissions.py
- test_tutor_retrieval.py
- compilerOptions
- tenants/permissions.py
- get_membership
- sms_providers.py
- TutorChat
- CiSmokeUser
- test_enterprise_gaps.py
- constants.py
- notifications/services.py
- _parse_stats
- sso_views.py
- CookieTokenRefreshView
- Command
- test_api.py
- test_sms.py
- scripts
- validate_http_url
- TestOrganizationInvites
- TestNotifications
- helpers.js
- main.jsx
- ErrorBoundary.jsx
- Command
- TenantsConfig
- TestTutorChat
- TestUserRoleUpdate
- Command
- base.py
- TestMediaLibraryApi
- TestSmsAlerts
- package.json
- AccountsConfig
- BillingConfig
- LearningConfig
- 0003_migrate_primary_color_to_green.py
- TestPushAdmin
- jwt.js
- vercel.json
- AnalyticsConfig
- AuditConfig
- ForumConfig
- NotificationsConfig
- QuizzesConfig
- TutorConfig
- TestAuditLogs
- TestInAppBroadcast
- TestCertificateTask
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
- globals
- @sentry/react
- @testing-library/user-event
- vite
- vite-plugin-pwa
- @vitejs/plugin-react
- vitest
- @vitest/coverage-v8
- NotFoundPage.jsx
- upload_file
- TestLearningProgress
- Civic Education Platform API Reference
- TestTopicModeration
- TestSsoStatus
- 2. Stripe billing (required)
- 5. AI tutor — Anthropic (optional)
- .save
- TestHealthCheck
- TestQuizI18n
- TestAnalytics
- TestForum
- 0009_learning_progress.py
- TestQuizOptionsI18n
- eslint
- eslint-plugin-react-refresh
- jsdom
- tailwindcss
- @testing-library/jest-dom
- @testing-library/react
- constants.py
- TestMediaLibraryApi
- TestEngagement
- EngagementConfig
- GamificationConfig
- TestIntegrationsStatusEndpoint
- TestGamification
- TestGlobalSearch
- TestTutorHistory
- TestPendingQueue
- TestOrgRoleRBAC
- TestPendingQueue
- TestQuizzes
- TestCertificateTask
- TestTutorAdminUsage
- 0006_userprofile_xp_points.py
- engagement/migrations/0001_initial.py
- gamification/migrations/0001_initial.py
- 0010_article_tutor_index_text_mediaasset_captions_url.py
- TestTutorStream
- MessageSerializer

## God Nodes (most connected - your core abstractions)
1. `bind_client_to_org()` - 110 edges
2. `get_current_organization()` - 93 edges
3. `Membership` - 81 edges
4. `log_activity()` - 72 edges
5. `Role` - 71 edges
6. `Organization` - 60 edges
7. `extractError()` - 53 edges
8. `OrganizationInvite` - 43 edges
9. `Article` - 41 edges
10. `Subscription` - 39 edges

## Surprising Connections (you probably didn't know these)
- `Command` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/management/commands/demote_legacy_org_admins.py → backend/apps/accounts/models.py
- `Command` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/management/commands/seed_data.py → backend/apps/accounts/models.py
- `Meta` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/serializers.py → backend/apps/accounts/models.py
- `RoleSerializer` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/serializers.py → backend/apps/accounts/models.py
- `UserProfileSerializer` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/serializers.py → backend/apps/accounts/models.py

## Import Cycles
- None detected.

## Communities (241 total, 100 thin omitted)

### Community 0 - "accounts/views.py"
Cohesion: 0.25
Nodes (39): AnonRateThrottle, Role, PasswordResetConfirmSerializer, PasswordResetOtpConfirmSerializer, PasswordResetOtpRequestSerializer, PasswordResetRequestSerializer, PhoneVerifyConfirmSerializer, ProfileUpdateSerializer (+31 more)

### Community 1 - "log_activity"
Cohesion: 0.09
Nodes (28): JWTCookieAuthentication, Cookie-aware JWT authentication.  Checks httpOnly cookies first (preferred, mo, Authenticate via httpOnly cookie if present; fall back to Bearer header., check_session_idle(), is_privileged_user(), Server-side session controls: idle timeout and epoch-based revocation., Privileged sessions enforce idle timeout (platform staff or org admins)., Raise AuthenticationFailed if a privileged user has been idle too long. (+20 more)

### Community 2 - "quizzes/views.py"
Cohesion: 0.08
Nodes (31): get_preferred_language(), Resolve API content language to ``en`` or ``ar`` only., notify_user(), Create a single notification for one user (cheap, stays inline)., Certificate, Meta, Question, Quiz (+23 more)

### Community 3 - "get_current_organization"
Cohesion: 0.14
Nodes (22): IsOrgAnalyticsAdmin, BasePermission, Organization owner or admin (analytics plan checked in the view)., build_my_learning_summary(), Personal learning dashboard for the current user in the active organization., AnalyticsForumView, AnalyticsLearningView, AnalyticsOverviewView (+14 more)

### Community 4 - "sso.py"
Cohesion: 0.07
Nodes (48): build_authorize_url(), claims_from_tokens(), exchange_code_for_tokens(), _fetch_jwks(), fetch_oidc_metadata(), fetch_userinfo(), get_or_create_user_from_sso(), get_org_sso_config() (+40 more)

### Community 5 - "ui.jsx"
Cohesion: 0.11
Nodes (30): Pagination(), Alert(), CardSkeleton(), ConfirmDialog(), EmptyState(), ORG_ROLE_STYLES, PageHeader(), ROLE_STYLES (+22 more)

### Community 6 - "forum/views.py"
Cohesion: 0.12
Nodes (19): DiscussionComment, DiscussionTopic, Meta, CommentCreateSerializer, DiscussionCommentSerializer, DiscussionTopicCreateSerializer, DiscussionTopicSerializer, Meta (+11 more)

### Community 7 - "Membership"
Cohesion: 0.07
Nodes (22): _client_meta(), compute_integrity_hash(), log_activity(), Verify hash-chain integrity for recent activity logs., verify_audit_chain(), MediaAssetViewSet, AuditIntegrityVerifyView, ComplianceEvidencePackView (+14 more)

### Community 8 - "ProfilePage.jsx"
Cohesion: 0.17
Nodes (24): OfflineBanner(), useOnlineStatus(), api, fetchOrCache(), listCacheKey(), loadArticle(), loadArticlesList(), loadCategories() (+16 more)

### Community 9 - "OrganizationInvite"
Cohesion: 0.12
Nodes (22): normalize_primary_color(), Return green default when ``color`` is a legacy blue brand value., BulkMemberImportView, DepartmentDetailView, OrganizationSsoConfigView, Enterprise org APIs: SSO config, departments, bulk import, platform org console., Department, Meta (+14 more)

### Community 10 - "bind_client_to_org"
Cohesion: 0.15
Nodes (6): bind_client_to_org(), Authenticate and scope requests to ``org`` (creates membership if needed)., TestArticles, TestPlatformSupportAndSecurity, TestQuizI18n, TestEngagement

### Community 11 - "BillingPage.jsx"
Cohesion: 0.08
Nodes (21): AuthShell(), PlatformLogo(), PasswordInput(), passwordStrength(), PasswordStrengthBar(), UsageBar(), authService, billingService (+13 more)

### Community 12 - "App.jsx"
Cohesion: 0.05
Nodes (35): AcceptInvitePage, AdminPage, ArticleDetailPage, ArticleEditorPage, ArticlesManagePage, ArticlesPage, BillingPage, CategoriesManagePage (+27 more)

### Community 13 - "useAuth"
Cohesion: 0.07
Nodes (34): Breadcrumb(), EmailVerifyBanner(), ArrowUp(), ChevronRight(), Moon(), Sun(), InstallPrompt(), Layout() (+26 more)

### Community 14 - "core/middleware.py"
Cohesion: 0.08
Nodes (15): client_ip_from_request(), ip_allowed(), IP allowlist helpers and read-replica database router., Return True when allowlist is empty or client_ip matches an entry., Route reads to DATABASES['replica'] when configured., ReadReplicaRouter, ContentSecurityPolicyMiddleware, IpAllowlistMiddleware (+7 more)

### Community 15 - "extractError"
Cohesion: 0.15
Nodes (18): FEATURES, AcademicCap(), Bell(), BookOpen(), ChatBubble(), ChevronLeft(), CloudArrowDown(), Eye() (+10 more)

### Community 16 - "Subscription"
Cohesion: 0.33
Nodes (13): Plan, A subscription tier with pricing and per-tenant quotas., CheckoutSerializer, Meta, PlanSerializer, SubscriptionSerializer, BillingPortalView, CheckoutView (+5 more)

### Community 17 - "ArticleDetailPage.jsx"
Cohesion: 0.17
Nodes (13): MediaPlayer(), plainTextExcerpt(), renderMarkdown(), SANITIZE_OPTIONS, API_ORIGIN, resolveMediaUrl(), getEmbedInfo(), ArticleDetailPage() (+5 more)

### Community 18 - "Organization"
Cohesion: 0.15
Nodes (10): Command, BaseCommand, ActivityLog, Meta, ActivityLogSerializer, Meta, ActivityLogExportView, ActivityLogListView (+2 more)

### Community 19 - "notifications/views.py"
Cohesion: 0.16
Nodes (19): BroadcastNotificationSerializer, WebPushSubscribeSerializer, Notification, cleanup_push_subscriptions(), push_subscription_stats(), notify_all_users(), Fan out a notification to all active users via a background task.      When ``, cleanup_push_subscriptions_task() (+11 more)

### Community 20 - "enterprise_views.py"
Cohesion: 0.20
Nodes (27): OrganizationInvite, Pending email invitation to join an organization., IsOrgOwnerOrAdmin, InvitePreviewSerializer, MemberInviteSerializer, MemberRoleUpdateSerializer, MembershipSerializer, OrganizationInviteSerializer (+19 more)

### Community 21 - "conftest.py"
Cohesion: 0.12
Nodes (9): admin_user(), enable_mfa(), org(), Enroll a test user in TOTP MFA (privileged routes require this)., Default tenant; citizen_user is owner., TestContentPacks, TestMarkdownXss, TestMfaEnforcement (+1 more)

### Community 22 - "Icons.jsx"
Cohesion: 0.14
Nodes (21): LanguageSwitcher(), applyDirection(), initial, normalizeLanguage(), RTL_LANGUAGES, sanitizeStoredLanguage(), SUPPORTED_LANGUAGES, contentLanguage() (+13 more)

### Community 23 - "SmsMessage"
Cohesion: 0.18
Nodes (12): get_signed_url(), get_supabase_client(), _local_media_url(), _save_local_file(), upload_bytesio(), upload_file(), ArticleAttachmentUploadView, ArticleImageUploadView (+4 more)

### Community 24 - "billing/services.py"
Cohesion: 0.19
Nodes (18): AnalyticsNotAvailable, check_quota(), count_usage(), ensure_subscription(), get_active_plan(), get_default_plan(), get_subscription(), invalidate_quota_cache() (+10 more)

### Community 25 - "Notification"
Cohesion: 0.13
Nodes (7): SmsMessageAdmin, WebPushSubscriptionAdmin, WebPushSubscription, TestPhoneVerification, TestResendVerificationEmail, TestUnsuspendUser, TestWebPushSubscribe

### Community 26 - "tutor/services.py"
Cohesion: 0.06
Nodes (62): normalize_language(), Shared application constants., Return ``en`` or ``ar``; any other value maps to ``en``., get_user_organization(), Return the user's primary organization (first membership), or None., TutorChatAdmin, Meta, DB-backed per-user daily message counter. Redis is used as a fast     write-thr (+54 more)

### Community 27 - "test_saas.py"
Cohesion: 0.09
Nodes (13): AbstractBaseUser, User, CheckoutResult, TestCitizenRegistration, An article cannot reference a category that belongs to a different org., Org switcher: header selects another org the user belongs to., The tenant middleware must ignore X-Tenant-Slug for orgs the user         doesn, TestBilling (+5 more)

### Community 28 - "dependencies"
Cohesion: 0.08
Nodes (25): axios, dompurify, dependencies, axios, dompurify, i18next, i18next-browser-languagedetector, idb (+17 more)

### Community 29 - "Article"
Cohesion: 0.11
Nodes (17): Article, Category, Unified keyword search across published learning content and forum topics., CategorySerializer, MediaAssetSerializer, MediaAssetSummarySerializer, Meta, Compact nested representation for articles. (+9 more)

### Community 30 - "grade_a_views.py"
Cohesion: 0.16
Nodes (11): _attempts_queryset(), build_dashboard_summary(), build_institutional_report_pdf(), build_member_progress(), build_progress_csv(), org_member_users(), _parse_date(), parse_report_dates() (+3 more)

### Community 31 - "SecurityEvent"
Cohesion: 0.08
Nodes (39): build_integrations_report(), check_anthropic(), check_cache(), check_celery(), check_database(), check_email(), check_oidc(), check_pypdf() (+31 more)

### Community 32 - "localizedContent.js"
Cohesion: 0.08
Nodes (44): absolute_media_url(), Command, load_constitution_text(), BaseCommand, Prefer official PDF in seed_assets/ if present, else sample., resolve_constitution_attachment(), Campaign, Meta (+36 more)

### Community 33 - "devDependencies"
Cohesion: 0.09
Nodes (23): autoprefixer, @eslint/js, eslint-plugin-react-hooks, devDependencies, autoprefixer, @eslint/js, eslint-plugin-react-hooks, globals (+15 more)

### Community 34 - "BaseBillingProvider"
Cohesion: 0.12
Nodes (6): BaseBillingProvider, DummyBillingProvider, get_billing_provider(), Pluggable billing providers.  The ``dummy`` provider requires no external serv, No-op provider for local dev/tests; activates plans instantly., StripeBillingProvider

### Community 35 - "sms_views.py"
Cohesion: 0.14
Nodes (26): require_sms(), SmsMessage, normalize_phone(), Normalize to E.164 for South Sudan (+211)., BroadcastSmsSerializer, Meta, SendSmsSerializer, SmsMessageSerializer (+18 more)

### Community 36 - "MediaAssetSerializer"
Cohesion: 0.23
Nodes (8): CanDeleteOrgContent, IsOrgContentEditor, IsOrgForumModerator, IsOrgMember, BasePermission, Articles/quizzes: platform editor/admin OR org owner/admin/content_manager., Forum moderation: platform moderator/admin OR org owner/admin/moderator., Destructive content ops: platform admin OR org owner/admin.

### Community 37 - "learning/views.py"
Cohesion: 0.19
Nodes (4): bump_session_epoch(), Invalidate all outstanding JWTs for this user by advancing session_epoch., _get_managed_user(), Resolve a user visible in the current admin/moderator list.

### Community 38 - "tutor/views.py"
Cohesion: 0.11
Nodes (19): Send an email asynchronously with retry and logging.      Replaces fail_silent, send_email_task(), MembershipAdmin, OrganizationAdmin, OrganizationInviteAdmin, Membership, Organization, A tenant. All customer data is isolated per organization. (+11 more)

### Community 39 - "fan_out.py"
Cohesion: 0.16
Nodes (14): _get_or_create_prefs(), notify_user(), Unified notification fan-out.  Call :func:`notify_user` to deliver a notificat, Create an in-app Notification and fan-out to configured channels.      Returns, Fire-and-forget async send to the user's WebSocket group., _sms_push(), _web_push(), _ws_push() (+6 more)

### Community 40 - "session.py"
Cohesion: 0.27
Nodes (10): IsAdmin, IsCitizenOrAbove, IsEditor, IsEditorOrAdmin, IsModerator, IsModeratorOrAdmin, IsOwnerOrAdmin, BasePermission (+2 more)

### Community 41 - "Command"
Cohesion: 0.10
Nodes (24): consume_mfa_challenge(), generate_totp_secret(), issue_mfa_challenge(), provisioning_uri(), TOTP multi-factor authentication for privileged accounts., Platform admins and organization owners/admins must use MFA when org requires it, totp_for_secret(), user_has_mfa_enabled() (+16 more)

### Community 42 - "apply_subscription_updated"
Cohesion: 0.17
Nodes (11): apply_checkout_completed(), _apply_plan_code(), apply_subscription_deleted(), apply_subscription_updated(), plan_code_for_stripe_price(), Sync subscription after Stripe Checkout completes., Sync plan/status when Stripe subscription changes., Downgrade to the free plan when a paid subscription ends. (+3 more)

### Community 44 - "services.js"
Cohesion: 0.12
Nodes (24): TabList(), TabPanel(), AuthContext, OrganizationContext, OrganizationProvider(), pendingQueue, tenantStore, tokenStore (+16 more)

### Community 45 - "NotificationConsumer"
Cohesion: 0.15
Nodes (9): AsyncWebsocketConsumer, _group_name(), NotificationConsumer, WebSocket consumer for real-time in-app notifications.  Each authenticated use, Push a notification dict to all WebSocket connections for ``user_pk``.      Ca, WebSocket endpoint: /ws/notifications/      Authenticate via:     - ``?token=, Receive a notification event from the channel layer and forward         it to t, send_notification_to_user() (+1 more)

### Community 46 - "CivicUser"
Cohesion: 0.13
Nodes (4): CivicUser, HttpUser, Locust load test for the Civic Education Platform API.  Simulates the read-hea, Register and log in a unique user, then cache the auth header.

### Community 47 - "Command"
Cohesion: 0.29
Nodes (4): Command, BaseCommand, Path, Disaster-recovery restore drill.  Creates a logical backup of the current data

### Community 48 - "test_deploy.py"
Cohesion: 0.12
Nodes (14): CoreConfig, AppConfig, production_security_checks(), Validate settings required for a safe production deployment., Helpers for building Django ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS lists., Split comma-separated host strings and return de-duplicated hosts., unique_hosts(), Deployment readiness checks (production settings validation). (+6 more)

### Community 49 - "core/permissions.py"
Cohesion: 0.16
Nodes (12): get_session_epoch(), EmailTokenObtainPairSerializer, login_user(), Log in via API, completing MFA when enrolled., Grade-A enterprise: sessions, SCIM, compliance, support, IP allowlist., TestAuditIntegrity, TestIpAllowlist, TestScimProvisioning (+4 more)

### Community 50 - "test_tutor_retrieval.py"
Cohesion: 0.07
Nodes (34): maintain_tutor_index(), notify_on_publish(), build_tutor_index_text(), Build and maintain pre-indexed tutor search text on articles., Combine article body and PDF attachment text for tutor retrieval., _cache_key(), extract_pdf_text(), fetch_attachment_bytes() (+26 more)

### Community 51 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, baseUrl, checkJs, jsx, module, moduleResolution, target, types (+4 more)

### Community 52 - "tenants/permissions.py"
Cohesion: 0.10
Nodes (20): 10. Ongoing operations, 11. Organization invites, 12. Error monitoring (Sentry), 13. Database backups, 14. E2E testing, 1. Domain and TLS, 2. Backend secrets, 3. Database (+12 more)

### Community 53 - "get_membership"
Cohesion: 0.09
Nodes (13): EmailVerificationToken, Meta, PhoneOTP, UserProfile, Meta, RoleSerializer, UserProfileSerializer, verify_phone_otp() (+5 more)

### Community 54 - "sms_providers.py"
Cohesion: 0.29
Nodes (6): AfricasTalkingSmsProvider, BaseSmsProvider, DummySmsProvider, get_sms_provider(), Log SMS in development; always succeeds., SmsSendResult

### Community 55 - "TutorChat"
Cohesion: 0.16
Nodes (3): ArticleSerializer, _can_publish_directly(), ArticleViewSet

### Community 56 - "CiSmokeUser"
Cohesion: 0.10
Nodes (20): MediaAssetFilter, MediaAudioUploadView, MediaVideoUploadView, Meta, APIView, Media library API: CRUD + audio/video uploads., _upload_media_file(), ArticleProgress (+12 more)

### Community 57 - "test_enterprise_gaps.py"
Cohesion: 0.14
Nodes (6): check_mfa_enrolled(), Raise ``MfaSetupRequired`` when a privileged user has not enrolled MFA., _can_see_unpublished(), _can_see_unpublished(), get_membership(), _platform_role_name()

### Community 58 - "constants.py"
Cohesion: 0.06
Nodes (33): 10. Compliance / monitoring gates (production), 1. Celery + Redis (required), 2. Stripe billing (required), 3. SMS — Africa's Talking (optional), 4. Web push — VAPID (optional), 5. AI tutor — Anthropic (optional), 6. Enterprise SSO — OpenID Connect (optional), 7. Pre-flight validation (+25 more)

### Community 59 - "notifications/services.py"
Cohesion: 0.18
Nodes (3): CiSmokeUser, HttpUser, Lightweight Locust scenario for CI — avoids mass registration throttling.

### Community 60 - "_parse_stats"
Cohesion: 0.29
Nodes (8): main(), _parse_stats(), Path, Headless Locust smoke gate for CI.  Runs a short read-heavy scenario and fails, Return fail_ratio, p95_ms, failures, requests from Locust CSV stats., Path, Unit tests for Locust CI gate stats parsing (no live Locust run)., test_parse_stats_aggregated()

### Community 62 - "CookieTokenRefreshView"
Cohesion: 0.22
Nodes (6): CookieAwareTokenRefreshSerializer, CookieTokenRefreshView, Cookie-aware JWT refresh — accepts refresh from body or httpOnly cookie., Refresh access tokens using body or the httpOnly refresh cookie., TokenRefreshSerializer, TokenRefreshView

### Community 63 - "Command"
Cohesion: 0.31
Nodes (4): Command, BaseCommand, Path, Create a PostgreSQL logical backup using pg_dump.

### Community 65 - "test_sms.py"
Cohesion: 0.31
Nodes (6): APIView, SsoCallbackView, SsoLoginView, SsoStatusView, plan_has_sso(), require_sso()

### Community 66 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, lint, preview, test, test:e2e, test:e2e:live (+1 more)

### Community 67 - "validate_http_url"
Cohesion: 0.16
Nodes (10): DepartmentListCreateView, _org_support_snapshot(), PlatformOrganizationDetailView, PlatformOrganizationListView, PlatformUsageSummaryView, APIView, Platform admin: list/search all tenants., Platform admin: activate/deactivate or view read-only support metrics. (+2 more)

### Community 70 - "helpers.js"
Cohesion: 0.31
Nodes (6): apiGlob(), liveAuthHeaders(), loginLive(), mockSession(), seedLiveAuth(), TUTOR_DONE

### Community 71 - "main.jsx"
Cohesion: 0.38
Nodes (4): App(), guard(), queryClient, initSentry()

### Community 73 - "Command"
Cohesion: 0.33
Nodes (3): Command, BaseCommand, Management command: report English/Arabic bilingual content completeness.  Usa

### Community 74 - "TenantsConfig"
Cohesion: 0.33
Nodes (3): AppConfig, TenantsConfig, Tenant signal handlers.  Subscription provisioning on organization creation li

### Community 76 - "TestUserRoleUpdate"
Cohesion: 0.17
Nodes (12): Background tasks (Celery + Redis), CI load-test gate, CI load-test gate, Eager fallback (dev / test), Getting meaningful numbers, Headless ramp toward the SRS concurrency target, Institutional scale notes (10k concurrent), Load testing (Locust) (+4 more)

### Community 77 - "Command"
Cohesion: 0.15
Nodes (13): AI tutor (RAG), API reference, Backend setup, Background tasks (Celery), Civic Education Platform, Default accounts (after `seed_data`), Deployment (Render), Load testing (+5 more)

### Community 78 - "base.py"
Cohesion: 0.31
Nodes (8): GamificationSummary(), StatCardSkeleton(), StatTile(), gamificationService, activityLink(), DashboardPage(), formatDate(), LearnerDashboard()

### Community 81 - "package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 83 - "BillingConfig"
Cohesion: 0.22
Nodes (8): Civic Education Platform — Frontend, Deployment, Environment variables, Features, Local setup, Project structure, Requirements, Scripts

### Community 89 - "vercel.json"
Cohesion: 0.50
Nodes (3): buildCommand, outputDirectory, rewrites

### Community 96 - "TestAuditLogs"
Cohesion: 0.17
Nodes (12): 1. Add source files, 2. Run seed, 3. Verify, API path, Constitution & controlled documents, Option A — Seed data (recommended for demos), Option B — Article editor (production / org admins), Overview (+4 more)

### Community 98 - "TestCertificateTask"
Cohesion: 0.17
Nodes (12): AI Tutor — RAG & PDF grounding, API endpoints, Constitution & PDF content, Dependencies, Frontend, GET `/api/tutor/usage/platform/` — platform admin, How retrieval works, Limits & caching (+4 more)

### Community 142 - "globals"
Cohesion: 0.25
Nodes (8): Certification readiness, Content governance & reporting, Enterprise features (Government / NGO), Grade-A controls (summary), Identity provisioning, Org structure & scale, Production ops, Security & compliance

### Community 143 - "@sentry/react"
Cohesion: 0.62
Nodes (6): buildPayload(), emptyQuestion(), optionsArMismatch(), optionsFromText(), questionFromApi(), QuizEditorPage()

### Community 145 - "vite"
Cohesion: 0.33
Nodes (6): Compliance readiness (SOC 2 / ISO 27001), Control matrix, Evidence pack (in-product), Production security baseline (must be true before audit), Recurring ops (auditor will ask), What certification still requires (outside this repo)

### Community 146 - "vite-plugin-pwa"
Cohesion: 0.33
Nodes (6): Automated backup, CI, Disaster recovery, Manual restore (true incident), Restore drill (required before audits), RPO / RTO targets (ops commitment)

### Community 148 - "vitest"
Cohesion: 0.10
Nodes (9): PlanAdmin, SubscriptionAdmin, BillingConfig, AppConfig, Meta, Subscription, create_default_subscription(), Every new organization starts on the default (free) plan. (+1 more)

### Community 196 - "upload_file"
Cohesion: 0.14
Nodes (12): clear_current_organization(), organization_context(), Per-request tenant context.  The current organization is stored in a context v, Temporarily run a block scoped to ``organization`` (e.g. in tasks/tests)., set_current_organization(), Manager that automatically scopes queries to the current organization.      Wh, TenantManager, TenantQuerySet (+4 more)

### Community 198 - "Civic Education Platform API Reference"
Cohesion: 0.29
Nodes (7): Civic Education Platform API Reference, Conventions, Endpoint index, Gamification & engagement, Ops commands, Related docs, Tutor API (summary)

### Community 200 - "TestSsoStatus"
Cohesion: 0.50
Nodes (3): broadcast_notification_task(), Fan out an in-app notification to active users in batches., TestBroadcastTask

### Community 201 - "2. Stripe billing (required)"
Cohesion: 0.20
Nodes (10): Backend tests, CI pipeline (`.github/workflows/ci.yml`), E2E tests (Playwright), Environment variables (live e2e), Frontend unit tests (Vitest), Live backend (`e2e-live` CI job), Mocked API (default — `frontend` CI job), Ops smoke (loadtest job) (+2 more)

### Community 202 - "5. AI tutor — Anthropic (optional)"
Cohesion: 0.32
Nodes (5): global_search(), Scope search to the request tenant, defaulting to the public workspace., _resolve_search_organization(), GlobalSearchView, APIView

## Knowledge Gaps
- **285 isolated node(s):** `Migration`, `Migration`, `Migration`, `Migration`, `Migration` (+280 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **100 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_current_organization()` connect `grade_a_views.py` to `quizzes/views.py`, `get_current_organization`, `Membership`, `OrganizationInvite`, `core/middleware.py`, `Subscription`, `Organization`, `notifications/views.py`, `enterprise_views.py`, `SmsMessage`, `tutor/services.py`, `Article`, `localizedContent.js`, `BaseBillingProvider`, `sms_views.py`, `MediaAssetSerializer`, `learning/views.py`, `tutor/views.py`, `Command`, `apply_subscription_updated`, `TutorChat`, `CiSmokeUser`, `test_enterprise_gaps.py`, `validate_http_url`, `upload_file`, `5. AI tutor — Anthropic (optional)`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `bind_client_to_org()` connect `bind_client_to_org` to `quizzes/views.py`, `forum/views.py`, `vitest`, `conftest.py`, `Notification`, `Article`, `SecurityEvent`, `localizedContent.js`, `tutor/views.py`, `Command`, `core/permissions.py`, `CiSmokeUser`, `TestOrganizationInvites`, `TestLearningProgress`, `TestTopicModeration`, `TestTutorChat`, `TestHealthCheck`, `TestAnalytics`, `TestMediaLibraryApi`, `TestQuizOptionsI18n`, `TestPushAdmin`, `jwt.js`, `constants.py`, `TestMediaLibraryApi`, `TestIntegrationsStatusEndpoint`, `TestGamification`, `TestGlobalSearch`, `TestTutorHistory`, `TestPendingQueue`, `TestOrgRoleRBAC`, `TestPendingQueue`, `TestInAppBroadcast`, `TestQuizzes`, `TestCertificateTask`, `TestTutorAdminUsage`, `TestTutorStream`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `Membership` connect `tutor/views.py` to `log_activity`, `quizzes/views.py`, `sso.py`, `forum/views.py`, `OrganizationInvite`, `Organization`, `enterprise_views.py`, `vitest`, `Notification`, `test_saas.py`, `Article`, `grade_a_views.py`, `SecurityEvent`, `localizedContent.js`, `sms_views.py`, `MediaAssetSerializer`, `Command`, `core/permissions.py`, `CiSmokeUser`, `upload_file`, `TestSmsAlerts`, `TestGlobalSearch`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `Membership` (e.g. with `MembershipAdmin` and `OrganizationAdmin`) actually correct?**
  _`Membership` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 53 inferred relationships involving `Role` (e.g. with `Command` and `Command`) actually correct?**
  _`Role` has 53 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Migration`, `Migration`, `Migration` to the rest of the system?**
  _285 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `log_activity` be split into smaller, more focused modules?**
  _Cohesion score 0.09250693802035152 - nodes in this community are weakly interconnected._