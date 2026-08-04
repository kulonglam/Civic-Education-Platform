# Graph Report - Civic Education Platform  (2026-08-04)

## Corpus Check
- 424 files · ~168,831 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2562 nodes · 6656 edges · 240 communities (142 shown, 98 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 1145 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c2194eb0`
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
- TestAuditLogs
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
- `Meta` --uses--> `SmsMessage`  [INFERRED]
  backend/apps/notifications/sms_serializers.py → backend/apps/notifications/models.py
- `Command` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/management/commands/seed_data.py → backend/apps/accounts/models.py
- `Meta` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/serializers.py → backend/apps/accounts/models.py
- `PasswordResetConfirmSerializer` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/serializers.py → backend/apps/accounts/models.py
- `PasswordResetOtpConfirmSerializer` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/serializers.py → backend/apps/accounts/models.py

## Import Cycles
- None detected.

## Communities (240 total, 98 thin omitted)

### Community 0 - "accounts/views.py"
Cohesion: 0.28
Nodes (41): AnonRateThrottle, PasswordResetConfirmSerializer, PasswordResetOtpConfirmSerializer, PasswordResetOtpRequestSerializer, PasswordResetRequestSerializer, PhoneVerifyConfirmSerializer, ProfileUpdateSerializer, RegisterSerializer (+33 more)

### Community 1 - "log_activity"
Cohesion: 0.09
Nodes (27): JWTCookieAuthentication, Cookie-aware JWT authentication.  Checks httpOnly cookies first (preferred, mo, Authenticate via httpOnly cookie if present; fall back to Bearer header., check_session_idle(), is_privileged_user(), Server-side session controls: idle timeout and epoch-based revocation., Privileged sessions enforce idle timeout (platform staff or org admins)., Raise AuthenticationFailed if a privileged user has been idle too long. (+19 more)

### Community 2 - "quizzes/views.py"
Cohesion: 0.05
Nodes (46): absolute_media_url(), Command, load_constitution_text(), BaseCommand, Prefer official PDF in seed_assets/ if present, else sample., resolve_constitution_attachment(), get_signed_url(), get_supabase_client() (+38 more)

### Community 3 - "get_current_organization"
Cohesion: 0.10
Nodes (32): IsOrgAnalyticsAdmin, BasePermission, Organization owner or admin (analytics plan checked in the view)., _attempts_queryset(), build_dashboard_summary(), build_institutional_report_pdf(), build_member_progress(), build_my_learning_summary() (+24 more)

### Community 4 - "sso.py"
Cohesion: 0.07
Nodes (48): build_authorize_url(), claims_from_tokens(), exchange_code_for_tokens(), _fetch_jwks(), fetch_oidc_metadata(), fetch_userinfo(), get_or_create_user_from_sso(), get_org_sso_config() (+40 more)

### Community 5 - "ui.jsx"
Cohesion: 0.11
Nodes (31): Pagination(), Alert(), CardSkeleton(), ConfirmDialog(), EmptyState(), ORG_ROLE_STYLES, PageHeader(), ROLE_STYLES (+23 more)

### Community 6 - "forum/views.py"
Cohesion: 0.12
Nodes (19): DiscussionComment, DiscussionTopic, Meta, CommentCreateSerializer, DiscussionCommentSerializer, DiscussionTopicCreateSerializer, DiscussionTopicSerializer, Meta (+11 more)

### Community 7 - "Membership"
Cohesion: 0.07
Nodes (23): compute_integrity_hash(), Verify hash-chain integrity for recent activity logs., verify_audit_chain(), Scope search to the request tenant, defaulting to the public workspace., _resolve_search_organization(), get_current_organization(), DepartmentDetailView, DepartmentListCreateView (+15 more)

### Community 8 - "ProfilePage.jsx"
Cohesion: 0.17
Nodes (24): OfflineBanner(), useOnlineStatus(), api, fetchOrCache(), listCacheKey(), loadArticle(), loadArticlesList(), loadCategories() (+16 more)

### Community 9 - "OrganizationInvite"
Cohesion: 0.13
Nodes (21): normalize_primary_color(), Return green default when ``color`` is a legacy blue brand value., BulkMemberImportView, OrganizationSsoConfigView, Enterprise org APIs: SSO config, departments, bulk import, platform org console., Department, Meta, OrganizationSsoConfig (+13 more)

### Community 10 - "bind_client_to_org"
Cohesion: 0.10
Nodes (8): bind_client_to_org(), Authenticate and scope requests to ``org`` (creates membership if needed)., TestArticles, TestEngagement, TestTutorStream, TestOrgAnalytics, TestCertificateTask, TestUserRoleUpdate

### Community 11 - "BillingPage.jsx"
Cohesion: 0.08
Nodes (21): AuthShell(), PlatformLogo(), PasswordInput(), passwordStrength(), PasswordStrengthBar(), UsageBar(), authService, billingService (+13 more)

### Community 12 - "App.jsx"
Cohesion: 0.05
Nodes (35): AcceptInvitePage, AdminPage, ArticleDetailPage, ArticleEditorPage, ArticlesManagePage, ArticlesPage, BillingPage, CategoriesManagePage (+27 more)

### Community 13 - "useAuth"
Cohesion: 0.07
Nodes (32): Breadcrumb(), EmailVerifyBanner(), ArrowUp(), ChevronRight(), Moon(), Sun(), InstallPrompt(), Layout() (+24 more)

### Community 14 - "core/middleware.py"
Cohesion: 0.08
Nodes (15): client_ip_from_request(), ip_allowed(), IP allowlist helpers and read-replica database router., Return True when allowlist is empty or client_ip matches an entry., Route reads to DATABASES['replica'] when configured., ReadReplicaRouter, ContentSecurityPolicyMiddleware, IpAllowlistMiddleware (+7 more)

### Community 15 - "extractError"
Cohesion: 0.15
Nodes (18): FEATURES, AcademicCap(), Bell(), BookOpen(), ChatBubble(), ChevronLeft(), CloudArrowDown(), Eye() (+10 more)

### Community 16 - "Subscription"
Cohesion: 0.21
Nodes (17): PlanAdmin, SubscriptionAdmin, Meta, Plan, A subscription tier with pricing and per-tenant quotas., Subscription, CheckoutSerializer, Meta (+9 more)

### Community 17 - "ArticleDetailPage.jsx"
Cohesion: 0.16
Nodes (14): MediaPlayer(), readingTime(), plainTextExcerpt(), renderMarkdown(), SANITIZE_OPTIONS, API_ORIGIN, resolveMediaUrl(), getEmbedInfo() (+6 more)

### Community 18 - "Organization"
Cohesion: 0.11
Nodes (7): bump_session_epoch(), Invalidate all outstanding JWTs for this user by advancing session_epoch., _get_managed_user(), Resolve a user visible in the current admin/moderator list., _client_meta(), log_activity(), TestBackfillAuditOrgs

### Community 19 - "notifications/views.py"
Cohesion: 0.18
Nodes (17): BroadcastNotificationSerializer, WebPushSubscribeSerializer, WebPushSubscription, cleanup_push_subscriptions(), push_subscription_stats(), cleanup_push_subscriptions_task(), BroadcastNotificationView, Meta (+9 more)

### Community 20 - "enterprise_views.py"
Cohesion: 0.23
Nodes (27): OrganizationInvite, Pending email invitation to join an organization., IsOrgOwnerOrAdmin, InvitePreviewSerializer, MemberInviteSerializer, MemberRoleUpdateSerializer, MembershipSerializer, OrganizationInviteSerializer (+19 more)

### Community 21 - "conftest.py"
Cohesion: 0.09
Nodes (11): admin_user(), enable_mfa(), login_user(), org(), Enroll a test user in TOTP MFA (privileged routes require this)., Log in via API, completing MFA when enrolled., Default tenant; citizen_user is owner., Org switcher: header selects another org the user belongs to. (+3 more)

### Community 22 - "Icons.jsx"
Cohesion: 0.14
Nodes (22): LanguageSwitcher(), applyDirection(), initial, normalizeLanguage(), RTL_LANGUAGES, sanitizeStoredLanguage(), SUPPORTED_LANGUAGES, contentLanguage() (+14 more)

### Community 23 - "SmsMessage"
Cohesion: 0.15
Nodes (18): Article, Category, CategorySerializer, MediaAssetSummarySerializer, Meta, Compact nested representation for articles., ArticleAttachmentUploadView, ArticleFilter (+10 more)

### Community 24 - "billing/services.py"
Cohesion: 0.14
Nodes (21): APIView, SsoCallbackView, SsoLoginView, SsoStatusView, AnalyticsNotAvailable, check_quota(), count_usage(), get_active_plan() (+13 more)

### Community 25 - "Notification"
Cohesion: 0.09
Nodes (14): Command, BaseCommand, ActivityLog, Meta, ActivityLogSerializer, Meta, ActivityLogExportView, ActivityLogListView (+6 more)

### Community 26 - "tutor/services.py"
Cohesion: 0.06
Nodes (62): normalize_language(), Shared application constants., Return ``en`` or ``ar``; any other value maps to ``en``., get_user_organization(), Return the user's primary organization (first membership), or None., TutorChatAdmin, Meta, DB-backed per-user daily message counter. Redis is used as a fast     write-thr (+54 more)

### Community 27 - "test_saas.py"
Cohesion: 0.09
Nodes (12): AbstractBaseUser, User, CheckoutResult, TestCitizenRegistration, An article cannot reference a category that belongs to a different org., The tenant middleware must ignore X-Tenant-Slug for orgs the user         doesn, TestBilling, TestMyOrganizations (+4 more)

### Community 28 - "dependencies"
Cohesion: 0.08
Nodes (25): axios, dompurify, dependencies, axios, dompurify, i18next, i18next-browser-languagedetector, idb (+17 more)

### Community 29 - "Article"
Cohesion: 0.21
Nodes (3): MediaAssetSerializer, validate_http_url(), TestMediaHttpUrlValidation

### Community 30 - "grade_a_views.py"
Cohesion: 0.26
Nodes (6): CanDeleteOrgContent, IsOrgContentEditor, IsOrgMember, BasePermission, Articles/quizzes: platform editor/admin OR org owner/admin/content_manager., Destructive content ops: platform admin OR org owner/admin.

### Community 31 - "SecurityEvent"
Cohesion: 0.08
Nodes (38): build_integrations_report(), check_anthropic(), check_cache(), check_celery(), check_database(), check_email(), check_oidc(), check_pypdf() (+30 more)

### Community 32 - "localizedContent.js"
Cohesion: 0.10
Nodes (38): Campaign, Meta, Petition, PetitionSignature, Poll, PollOption, PollVote, CampaignCreateSerializer (+30 more)

### Community 33 - "devDependencies"
Cohesion: 0.09
Nodes (23): autoprefixer, eslint, @eslint/js, eslint-plugin-react-hooks, devDependencies, autoprefixer, eslint, @eslint/js (+15 more)

### Community 34 - "BaseBillingProvider"
Cohesion: 0.12
Nodes (6): BaseBillingProvider, DummyBillingProvider, get_billing_provider(), Pluggable billing providers.  The ``dummy`` provider requires no external serv, No-op provider for local dev/tests; activates plans instantly., StripeBillingProvider

### Community 35 - "sms_views.py"
Cohesion: 0.20
Nodes (15): require_sms(), MessageSerializer, Generic ``{"message": "..."}`` response body., BroadcastSmsSerializer, Meta, SendSmsSerializer, SmsMessageSerializer, BroadcastSmsView (+7 more)

### Community 36 - "MediaAssetSerializer"
Cohesion: 0.24
Nodes (8): MediaAssetFilter, Meta, MediaAsset, Coverage-oriented tests for media–article linking and MediaAsset helpers., test_article_can_attach_audio_and_video(), test_article_rejects_wrong_media_type(), test_media_asset_playback_url_external(), test_media_asset_playback_url_prefers_upload()

### Community 37 - "learning/views.py"
Cohesion: 0.24
Nodes (7): _can_see_unpublished(), MediaAssetViewSet, MediaAudioUploadView, MediaVideoUploadView, APIView, Media library API: CRUD + audio/video uploads., _upload_media_file()

### Community 38 - "tutor/views.py"
Cohesion: 0.08
Nodes (24): MembershipAdmin, OrganizationAdmin, OrganizationInviteAdmin, Manager that automatically scopes queries to the current organization.      Wh, TenantManager, TenantQuerySet, Resolves the current tenant for each request.  Resolution order:     1. ``X-T, Membership (+16 more)

### Community 39 - "fan_out.py"
Cohesion: 0.12
Nodes (16): SmsMessageAdmin, WebPushSubscriptionAdmin, _get_or_create_prefs(), notify_user(), Unified notification fan-out.  Call :func:`notify_user` to deliver a notificat, Create an in-app Notification and fan-out to configured channels.      Returns, Fire-and-forget async send to the user's WebSocket group., _sms_push() (+8 more)

### Community 40 - "session.py"
Cohesion: 0.27
Nodes (12): SmsMessage, normalize_phone(), Normalize to E.164 for South Sudan (+211)., create_sms_log(), deliver_sms(), org_member_phones(), queue_sms_to_phone(), send_phone_verify_otp() (+4 more)

### Community 41 - "Command"
Cohesion: 0.13
Nodes (13): consume_mfa_challenge(), generate_totp_secret(), issue_mfa_challenge(), provisioning_uri(), TOTP multi-factor authentication for privileged accounts., Platform admins and organization owners/admins must use MFA when org requires it, totp_for_secret(), user_has_mfa_enabled() (+5 more)

### Community 42 - "apply_subscription_updated"
Cohesion: 0.17
Nodes (11): apply_checkout_completed(), _apply_plan_code(), apply_subscription_deleted(), apply_subscription_updated(), plan_code_for_stripe_price(), Sync subscription after Stripe Checkout completes., Sync plan/status when Stripe subscription changes., Downgrade to the free plan when a paid subscription ends. (+3 more)

### Community 44 - "services.js"
Cohesion: 0.12
Nodes (23): TabList(), TabPanel(), AuthContext, OrganizationContext, OrganizationProvider(), pendingQueue, tenantStore, tokenStore (+15 more)

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
Cohesion: 0.10
Nodes (22): CoreConfig, AppConfig, production_security_checks(), Validate settings required for a safe production deployment., Helpers for building Django ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS lists., Split comma-separated host strings and return de-duplicated hosts., Return the Render service hostname from platform-injected env vars., True when a Redis URL targets this machine (dev default, invalid on Render). (+14 more)

### Community 49 - "core/permissions.py"
Cohesion: 0.18
Nodes (12): Command, BaseCommand, Role, EmailTokenObtainPairSerializer, Grade-A enterprise: sessions, SCIM, compliance, support, IP allowlist., TestAuditIntegrity, TestIpAllowlist, TestScimProvisioning (+4 more)

### Community 50 - "test_tutor_retrieval.py"
Cohesion: 0.07
Nodes (38): maintain_tutor_index(), notify_on_publish(), build_tutor_index_text(), Build and maintain pre-indexed tutor search text on articles., Combine article body and PDF attachment text for tutor retrieval., notify_all_users(), Fan out a notification to all active users via a background task.      When ``, set_current_organization() (+30 more)

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
Cohesion: 0.14
Nodes (3): ArticleSerializer, _can_publish_directly(), ArticleViewSet

### Community 56 - "CiSmokeUser"
Cohesion: 0.23
Nodes (7): ArticleProgress, MediaProgress, Meta, Record and query learner progress on articles and media., record_article_progress(), record_media_progress(), _resolve_organization()

### Community 57 - "test_enterprise_gaps.py"
Cohesion: 0.14
Nodes (7): check_mfa_enrolled(), Raise ``MfaSetupRequired`` when a privileged user has not enrolled MFA., _can_see_unpublished(), get_membership(), IsOrgForumModerator, _platform_role_name(), Forum moderation: platform moderator/admin OR org owner/admin/moderator.

### Community 58 - "constants.py"
Cohesion: 0.06
Nodes (34): 10. Compliance / monitoring gates (production), 1. Celery + Redis (required), 2. Stripe billing (required for paid SaaS), 2b. No Stripe / unsupported country (e.g. Uganda), 3. SMS — Africa's Talking (optional), 4. Web push — VAPID (optional), 5. AI tutor — Anthropic (optional), 6. Enterprise SSO — OpenID Connect (optional) (+26 more)

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
Cohesion: 0.27
Nodes (10): IsAdmin, IsCitizenOrAbove, IsEditor, IsEditorOrAdmin, IsModerator, IsModeratorOrAdmin, IsOwnerOrAdmin, BasePermission (+2 more)

### Community 66 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, lint, preview, test, test:e2e, test:e2e:live (+1 more)

### Community 67 - "validate_http_url"
Cohesion: 0.21
Nodes (9): _org_support_snapshot(), PlatformOrganizationDetailView, PlatformOrganizationListView, PlatformUsageSummaryView, APIView, Platform admin: list/search all tenants., Platform admin: activate/deactivate or view read-only support metrics., Cross-org usage rollup for ministry-of-education style operators. (+1 more)

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

### Community 79 - "TestMediaLibraryApi"
Cohesion: 0.36
Nodes (4): global_search(), Unified keyword search across published learning content and forum topics., GlobalSearchView, APIView

### Community 80 - "TestSmsAlerts"
Cohesion: 0.22
Nodes (7): BillingConfig, AppConfig, ensure_subscription(), get_default_plan(), Return the org subscription, creating a free-plan row if missing., create_default_subscription(), Every new organization starts on the default (free) plan.

### Community 81 - "package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 83 - "BillingConfig"
Cohesion: 0.22
Nodes (8): Civic Education Platform — Frontend, Deployment, Environment variables, Features, Local setup, Project structure, Requirements, Scripts

### Community 87 - "jwt.js"
Cohesion: 0.50
Nodes (3): broadcast_notification_task(), Fan out an in-app notification to active users in batches., TestBroadcastTask

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

### Community 196 - "upload_file"
Cohesion: 0.25
Nodes (5): clear_current_organization(), organization_context(), Per-request tenant context.  The current organization is stored in a context v, Temporarily run a block scoped to ``organization`` (e.g. in tasks/tests)., TenantMiddleware

### Community 198 - "Civic Education Platform API Reference"
Cohesion: 0.29
Nodes (7): Civic Education Platform API Reference, Conventions, Endpoint index, Gamification & engagement, Ops commands, Related docs, Tutor API (summary)

### Community 201 - "2. Stripe billing (required)"
Cohesion: 0.20
Nodes (10): Backend tests, CI pipeline (`.github/workflows/ci.yml`), E2E tests (Playwright), Environment variables (live e2e), Frontend unit tests (Vitest), Live backend (`e2e-live` CI job), Mocked API (default — `frontend` CI job), Ops smoke (loadtest job) (+2 more)

### Community 203 - ".save"
Cohesion: 0.11
Nodes (13): custom_exception_handler(), MfaSetupRequired, APIException, Log permission denials and MFA setup blocks as security events., _client_ip(), log_security_event(), Any, Structured security event logging for monitoring and incident response. (+5 more)

## Knowledge Gaps
- **287 isolated node(s):** `Migration`, `Migration`, `Migration`, `Migration`, `Migration` (+282 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **98 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `bind_client_to_org()` connect `bind_client_to_org` to `quizzes/views.py`, `forum/views.py`, `Subscription`, `vitest`, `conftest.py`, `SmsMessage`, `Notification`, `Article`, `SecurityEvent`, `localizedContent.js`, `MediaAssetSerializer`, `tutor/views.py`, `Command`, `core/permissions.py`, `CiSmokeUser`, `test_api.py`, `TestOrganizationInvites`, `TestLearningProgress`, `TestTopicModeration`, `TestSsoStatus`, `.save`, `TestTutorChat`, `TestQuizOptionsI18n`, `TestPushAdmin`, `constants.py`, `TestMediaLibraryApi`, `TestEngagement`, `TestIntegrationsStatusEndpoint`, `TestGamification`, `TestAuditLogs`, `TestTutorHistory`, `TestPendingQueue`, `TestInAppBroadcast`, `TestPendingQueue`, `TestOrgRoleRBAC`, `TestQuizzes`, `TestTutorAdminUsage`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `get_current_organization()` connect `Membership` to `accounts/views.py`, `quizzes/views.py`, `get_current_organization`, `OrganizationInvite`, `core/middleware.py`, `Subscription`, `Organization`, `notifications/views.py`, `enterprise_views.py`, `SmsMessage`, `Notification`, `tutor/services.py`, `grade_a_views.py`, `localizedContent.js`, `BaseBillingProvider`, `sms_views.py`, `learning/views.py`, `tutor/views.py`, `session.py`, `apply_subscription_updated`, `TutorChat`, `CiSmokeUser`, `test_enterprise_gaps.py`, `upload_file`, `TestMediaLibraryApi`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `Membership` connect `tutor/views.py` to `accounts/views.py`, `log_activity`, `quizzes/views.py`, `get_current_organization`, `sso.py`, `forum/views.py`, `OrganizationInvite`, `Subscription`, `enterprise_views.py`, `conftest.py`, `vitest`, `SmsMessage`, `Notification`, `test_saas.py`, `Article`, `grade_a_views.py`, `localizedContent.js`, `MediaAssetSerializer`, `learning/views.py`, `session.py`, `Command`, `core/permissions.py`, `CiSmokeUser`, `test_enterprise_gaps.py`, `upload_file`, `.save`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `Membership` (e.g. with `MembershipAdmin` and `OrganizationAdmin`) actually correct?**
  _`Membership` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 53 inferred relationships involving `Role` (e.g. with `Command` and `Command`) actually correct?**
  _`Role` has 53 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Migration`, `Migration`, `Migration` to the rest of the system?**
  _287 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `log_activity` be split into smaller, more focused modules?**
  _Cohesion score 0.09292929292929293 - nodes in this community are weakly interconnected._