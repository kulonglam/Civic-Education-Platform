# Graph Report - .  (2026-07-25)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2083 nodes · 5557 edges · 197 communities (120 shown, 77 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 979 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d3482a85`
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
- ArticleSerializer
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
- eslint-plugin-react-hooks
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

## God Nodes (most connected - your core abstractions)
1. `bind_client_to_org()` - 90 edges
2. `get_current_organization()` - 81 edges
3. `Membership` - 78 edges
4. `log_activity()` - 72 edges
5. `Role` - 68 edges
6. `Organization` - 58 edges
7. `extractError()` - 48 edges
8. `OrganizationInvite` - 43 edges
9. `useAuth()` - 39 edges
10. `Subscription` - 37 edges

## Surprising Connections (you probably didn't know these)
- `Meta` --uses--> `SmsMessage`  [INFERRED]
  backend/apps/notifications/sms_serializers.py → backend/apps/notifications/models.py
- `Command` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/management/commands/seed_data.py → backend/apps/accounts/models.py
- `OidcCredentials` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/sso.py → backend/apps/accounts/models.py
- `ScimUserDetailView` --uses--> `Role`  [INFERRED]
  backend/apps/tenants/scim.py → backend/apps/accounts/models.py
- `ScimUsersView` --uses--> `Role`  [INFERRED]
  backend/apps/tenants/scim.py → backend/apps/accounts/models.py

## Import Cycles
- None detected.

## Communities (197 total, 77 thin omitted)

### Community 0 - "accounts/views.py"
Cohesion: 0.05
Nodes (93): AnonRateThrottle, Command, BaseCommand, consume_mfa_challenge(), generate_totp_secret(), issue_mfa_challenge(), provisioning_uri(), TOTP multi-factor authentication for privileged accounts. (+85 more)

### Community 1 - "log_activity"
Cohesion: 0.05
Nodes (36): bump_session_epoch(), Invalidate all outstanding JWTs for this user by advancing session_epoch., Command, BaseCommand, ActivityLog, Meta, ActivityLogSerializer, Meta (+28 more)

### Community 2 - "quizzes/views.py"
Cohesion: 0.08
Nodes (34): upload_bytesio(), get_preferred_language(), Resolve API content language to ``en`` or ``ar`` only., notify_user(), Create a single notification for one user (cheap, stays inline)., Certificate, Meta, Question (+26 more)

### Community 3 - "get_current_organization"
Cohesion: 0.07
Nodes (36): IsOrgAnalyticsAdmin, BasePermission, Organization owner or admin (analytics plan checked in the view)., _attempts_queryset(), build_dashboard_summary(), build_institutional_report_pdf(), build_member_progress(), build_progress_csv() (+28 more)

### Community 4 - "sso.py"
Cohesion: 0.07
Nodes (47): build_authorize_url(), claims_from_tokens(), exchange_code_for_tokens(), _fetch_jwks(), fetch_oidc_metadata(), fetch_userinfo(), get_or_create_user_from_sso(), get_org_sso_config() (+39 more)

### Community 5 - "ui.jsx"
Cohesion: 0.13
Nodes (29): Pagination(), Alert(), CardSkeleton(), ConfirmDialog(), EmptyState(), ORG_ROLE_STYLES, PageHeader(), ROLE_STYLES (+21 more)

### Community 6 - "forum/views.py"
Cohesion: 0.12
Nodes (19): DiscussionComment, DiscussionTopic, Meta, CommentCreateSerializer, DiscussionCommentSerializer, DiscussionTopicCreateSerializer, DiscussionTopicSerializer, Meta (+11 more)

### Community 7 - "Membership"
Cohesion: 0.09
Nodes (21): Send an email asynchronously with retry and logging.      Replaces fail_silent, send_email_task(), MembershipAdmin, OrganizationAdmin, OrganizationInviteAdmin, Membership, accept_organization_invite(), create_organization_with_owner() (+13 more)

### Community 8 - "ProfilePage.jsx"
Cohesion: 0.12
Nodes (31): CloudArrowDown(), Trophy(), OfflineBanner(), OrgRoleBadge(), RoleBadge(), useOnlineStatus(), api, fetchOrCache() (+23 more)

### Community 9 - "OrganizationInvite"
Cohesion: 0.21
Nodes (26): OrganizationInvite, Pending email invitation to join an organization., IsOrgMember, IsOrgOwnerOrAdmin, InvitePreviewSerializer, MemberInviteSerializer, MemberRoleUpdateSerializer, MembershipSerializer (+18 more)

### Community 10 - "bind_client_to_org"
Cohesion: 0.08
Nodes (11): bind_client_to_org(), Authenticate and scope requests to ``org`` (creates membership if needed)., TestArticles, TestQuizI18n, TestQuizOptionsI18n, TestPendingQueue, TestTopicModeration, TestOrgAnalytics (+3 more)

### Community 11 - "BillingPage.jsx"
Cohesion: 0.09
Nodes (21): AuthShell(), FEATURES, PlatformLogo(), PasswordInput(), passwordStrength(), PasswordStrengthBar(), UsageBar(), authService (+13 more)

### Community 12 - "App.jsx"
Cohesion: 0.06
Nodes (32): AcceptInvitePage, AdminPage, ArticleDetailPage, ArticleEditorPage, ArticlesManagePage, ArticlesPage, BillingPage, CategoriesManagePage (+24 more)

### Community 13 - "useAuth"
Cohesion: 0.14
Nodes (22): EmailVerifyBanner(), AcademicCap(), BookOpen(), ShieldCheck(), ProtectedRoute(), mockedUseAuth, mockUser, AuthContext (+14 more)

### Community 14 - "core/middleware.py"
Cohesion: 0.08
Nodes (15): client_ip_from_request(), ip_allowed(), IP allowlist helpers and read-replica database router., Return True when allowlist is empty or client_ip matches an entry., Route reads to DATABASES['replica'] when configured., ReadReplicaRouter, ContentSecurityPolicyMiddleware, IpAllowlistMiddleware (+7 more)

### Community 15 - "extractError"
Cohesion: 0.11
Nodes (22): ChevronLeft(), PushNotificationPrompt(), urlBase64ToUint8Array(), extractError(), pendingQueue, categoryService, CategoriesManagePage(), slugify() (+14 more)

### Community 16 - "Subscription"
Cohesion: 0.21
Nodes (17): PlanAdmin, SubscriptionAdmin, Meta, Plan, A subscription tier with pricing and per-tenant quotas., Subscription, CheckoutSerializer, Meta (+9 more)

### Community 17 - "ArticleDetailPage.jsx"
Cohesion: 0.12
Nodes (18): Breadcrumb(), ChevronRight(), MediaPlayer(), readingTime(), plainTextExcerpt(), renderMarkdown(), SANITIZE_OPTIONS, API_ORIGIN (+10 more)

### Community 18 - "Organization"
Cohesion: 0.17
Nodes (19): Manager that automatically scopes queries to the current organization.      Wh, TenantManager, TenantQuerySet, Department, Meta, Organization, OrganizationSsoConfig, A tenant. All customer data is isolated per organization. (+11 more)

### Community 19 - "notifications/views.py"
Cohesion: 0.18
Nodes (14): BroadcastNotificationSerializer, WebPushSubscribeSerializer, cleanup_push_subscriptions(), push_subscription_stats(), cleanup_push_subscriptions_task(), BroadcastNotificationView, NotificationListView, NotificationReadAllView (+6 more)

### Community 20 - "enterprise_views.py"
Cohesion: 0.11
Nodes (18): BulkMemberImportView, DepartmentDetailView, DepartmentListCreateView, _org_support_snapshot(), OrganizationSsoConfigView, PlatformOrganizationDetailView, PlatformOrganizationListView, PlatformUsageSummaryView (+10 more)

### Community 21 - "conftest.py"
Cohesion: 0.09
Nodes (10): admin_user(), enable_mfa(), login_user(), org(), Enroll a test user in TOTP MFA (privileged routes require this)., Log in via API, completing MFA when enrolled., Default tenant; citizen_user is owner., TestMarkdownXss (+2 more)

### Community 22 - "Icons.jsx"
Cohesion: 0.11
Nodes (17): ArrowUp(), Bell(), ChatBubble(), Eye(), EyeOff(), FileText(), Medal(), Megaphone() (+9 more)

### Community 23 - "SmsMessage"
Cohesion: 0.17
Nodes (15): SmsMessage, normalize_phone(), Normalize to E.164 for South Sudan (+211)., create_sms_log(), deliver_sms(), issue_phone_otp(), org_member_phones(), queue_sms_to_phone() (+7 more)

### Community 24 - "billing/services.py"
Cohesion: 0.14
Nodes (22): AnalyticsNotAvailable, check_quota(), count_usage(), ensure_subscription(), get_active_plan(), get_default_plan(), get_subscription(), invalidate_quota_cache() (+14 more)

### Community 25 - "Notification"
Cohesion: 0.12
Nodes (11): SmsMessageAdmin, WebPushSubscriptionAdmin, Meta, Notification, WebPushSubscription, Meta, NotificationSerializer, TestPhoneVerification (+3 more)

### Community 26 - "tutor/services.py"
Cohesion: 0.15
Nodes (20): get_user_organization(), Return the user's primary organization (first membership), or None., _build_api_messages(), _call_claude(), ClaudeTutorService, clear_session(), _daily_cache_key(), enforce_budget() (+12 more)

### Community 27 - "test_saas.py"
Cohesion: 0.11
Nodes (9): AbstractBaseUser, User, CheckoutResult, TestCitizenRegistration, TestBilling, TestMyOrganizations, TestOrganizationRegistration, TestQuotas (+1 more)

### Community 28 - "dependencies"
Cohesion: 0.08
Nodes (25): axios, dompurify, dependencies, axios, dompurify, i18next, i18next-browser-languagedetector, idb (+17 more)

### Community 29 - "Article"
Cohesion: 0.17
Nodes (14): Article, Category, MediaAsset, Meta, MediaAssetSummarySerializer, Meta, Compact nested representation for articles., ArticleFilter (+6 more)

### Community 30 - "grade_a_views.py"
Cohesion: 0.16
Nodes (15): AuditIntegrityVerifyView, ComplianceEvidencePackView, _hash_token(), PlatformSupportCaseListView, PlatformSupportCaseUpdateView, APIView, Grade-A enterprise APIs: SCIM tokens, compliance pack, support cases, SLO., Download a compliance evidence pack for audits (ISO/SOC-style evidence). (+7 more)

### Community 31 - "SecurityEvent"
Cohesion: 0.14
Nodes (15): Meta, Persisted security events for platform-admin monitoring dashboards., SecurityEvent, DetailSerializer, HealthSerializer, MessageSerializer, Generic ``{"detail": "..."}`` response body., Generic ``{"message": "..."}`` response body. (+7 more)

### Community 32 - "localizedContent.js"
Cohesion: 0.20
Nodes (17): LanguageSwitcher(), applyDirection(), initial, normalizeLanguage(), RTL_LANGUAGES, sanitizeStoredLanguage(), SUPPORTED_LANGUAGES, contentLanguage() (+9 more)

### Community 33 - "devDependencies"
Cohesion: 0.10
Nodes (21): autoprefixer, eslint, @eslint/js, eslint-plugin-react-refresh, devDependencies, autoprefixer, eslint, @eslint/js (+13 more)

### Community 34 - "BaseBillingProvider"
Cohesion: 0.12
Nodes (6): BaseBillingProvider, DummyBillingProvider, get_billing_provider(), Pluggable billing providers.  The ``dummy`` provider requires no external serv, No-op provider for local dev/tests; activates plans instantly., StripeBillingProvider

### Community 35 - "sms_views.py"
Cohesion: 0.22
Nodes (13): require_sms(), BroadcastSmsSerializer, Meta, SendSmsSerializer, SmsMessageSerializer, BroadcastSmsView, PlatformBroadcastSmsView, APIView (+5 more)

### Community 36 - "MediaAssetSerializer"
Cohesion: 0.15
Nodes (10): _can_see_unpublished(), MediaAssetFilter, MediaAssetViewSet, MediaAudioUploadView, MediaVideoUploadView, Meta, APIView, Media library API: CRUD + audio/video uploads. (+2 more)

### Community 37 - "learning/views.py"
Cohesion: 0.17
Nodes (11): CategorySerializer, ArticleAttachmentUploadView, ArticleImageUploadView, CategoryViewSet, content_bundle(), ContentBundleThrottle, APIView, UserRateThrottle (+3 more)

### Community 38 - "tutor/views.py"
Cohesion: 0.29
Nodes (12): ChatRequestSerializer, ChatResponseSerializer, TutorUsageSerializer, get_tutor_service(), UserRateThrottle, TutorRateThrottle, ChatView, ClearSessionView (+4 more)

### Community 39 - "fan_out.py"
Cohesion: 0.16
Nodes (14): Push a notification dict to all WebSocket connections for ``user_pk``.      Ca, send_notification_to_user(), _get_or_create_prefs(), notify_user(), Unified notification fan-out.  Call :func:`notify_user` to deliver a notificat, Create an in-app Notification and fan-out to configured channels.      Returns, Fire-and-forget async send to the user's WebSocket group., _sms_push() (+6 more)

### Community 40 - "session.py"
Cohesion: 0.19
Nodes (13): JWTCookieAuthentication, Cookie-aware JWT authentication.  Checks httpOnly cookies first (preferred, mo, Authenticate via httpOnly cookie if present; fall back to Bearer header., check_session_idle(), get_session_epoch(), is_privileged_user(), Server-side session controls: idle timeout and epoch-based revocation., Privileged sessions enforce idle timeout (platform staff or org admins). (+5 more)

### Community 41 - "Command"
Cohesion: 0.25
Nodes (6): absolute_media_url(), Command, load_constitution_text(), BaseCommand, Prefer official PDF in seed_assets/ if present, else sample., resolve_constitution_attachment()

### Community 42 - "apply_subscription_updated"
Cohesion: 0.17
Nodes (11): apply_checkout_completed(), _apply_plan_code(), apply_subscription_deleted(), apply_subscription_updated(), plan_code_for_stripe_price(), Sync subscription after Stripe Checkout completes., Sync plan/status when Stripe subscription changes., Downgrade to the free plan when a paid subscription ends. (+3 more)

### Community 43 - "ArticleSerializer"
Cohesion: 0.19
Nodes (3): ArticleSerializer, _can_publish_directly(), ArticleViewSet

### Community 44 - "services.js"
Cohesion: 0.21
Nodes (12): TabList(), TabPanel(), analyticsService, auditService, billingService, forumService, notificationService, notifyService (+4 more)

### Community 45 - "NotificationConsumer"
Cohesion: 0.17
Nodes (7): AsyncWebsocketConsumer, _group_name(), NotificationConsumer, WebSocket consumer for real-time in-app notifications.  Each authenticated use, WebSocket endpoint: /ws/notifications/      Authenticate via:     - ``?token=, Receive a notification event from the channel layer and forward         it to t, ASGI config for Civic Education Platform.  Handles both HTTP (via Django WSGI-

### Community 46 - "CivicUser"
Cohesion: 0.13
Nodes (4): CivicUser, HttpUser, Locust load test for the Civic Education Platform API.  Simulates the read-hea, Register and log in a unique user, then cache the auth header.

### Community 47 - "Command"
Cohesion: 0.29
Nodes (4): Command, BaseCommand, Path, Disaster-recovery restore drill.  Creates a logical backup of the current data

### Community 48 - "test_deploy.py"
Cohesion: 0.22
Nodes (9): CoreConfig, AppConfig, production_security_checks(), Validate settings required for a safe production deployment., Deployment readiness checks (production settings validation)., _run_checks(), test_production_checks_pass_with_valid_settings(), test_production_checks_reject_dummy_billing() (+1 more)

### Community 49 - "core/permissions.py"
Cohesion: 0.24
Nodes (10): IsAdmin, IsCitizenOrAbove, IsEditor, IsEditorOrAdmin, IsModerator, IsModeratorOrAdmin, IsOwnerOrAdmin, BasePermission (+2 more)

### Community 50 - "test_tutor_retrieval.py"
Cohesion: 0.29
Nodes (9): chunk_text(), format_retrieved_context(), Lightweight retrieval over published articles for the AI tutor.  Uses simple k, Return top-scoring chunks from published tenant articles.      Controlled docu, retrieve_article_chunks(), score_chunk(), _tokenize(), _build_system_prompt() (+1 more)

### Community 51 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, baseUrl, checkJs, jsx, module, moduleResolution, target, types (+4 more)

### Community 52 - "tenants/permissions.py"
Cohesion: 0.23
Nodes (7): CanDeleteOrgContent, IsOrgContentEditor, IsOrgForumModerator, BasePermission, Articles/quizzes: platform editor/admin OR org owner/admin/content_manager., Forum moderation: platform moderator/admin OR org owner/admin/moderator., Destructive content ops: platform admin OR org owner/admin.

### Community 53 - "get_membership"
Cohesion: 0.20
Nodes (3): _can_see_unpublished(), get_membership(), _platform_role_name()

### Community 54 - "sms_providers.py"
Cohesion: 0.29
Nodes (6): AfricasTalkingSmsProvider, BaseSmsProvider, DummySmsProvider, get_sms_provider(), Log SMS in development; always succeeds., SmsSendResult

### Community 55 - "TutorChat"
Cohesion: 0.25
Nodes (6): TutorChatAdmin, Meta, DB-backed per-user daily message counter. Redis is used as a fast     write-thr, TutorChat, TutorDailyUsage, persist_chat_messages_task()

### Community 56 - "CiSmokeUser"
Cohesion: 0.18
Nodes (3): CiSmokeUser, HttpUser, Lightweight Locust scenario for CI — avoids mass registration throttling.

### Community 57 - "test_enterprise_gaps.py"
Cohesion: 0.18
Nodes (4): Tests for remaining enterprise gaps: org RBAC, content packs, platform support., TestContentPacks, TestOrgRoleRBAC, TestPlatformSupportAndSecurity

### Community 58 - "constants.py"
Cohesion: 0.22
Nodes (6): normalize_language(), normalize_primary_color(), Shared application constants., Return ``en`` or ``ar``; any other value maps to ``en``., Return green default when ``color`` is a legacy blue brand value., _user_language()

### Community 59 - "notifications/services.py"
Cohesion: 0.27
Nodes (6): notify_on_publish(), notify_all_users(), Fan out a notification to all active users via a background task.      When ``, broadcast_notification_task(), Fan out an in-app notification to active users in batches., TestBroadcastTask

### Community 60 - "_parse_stats"
Cohesion: 0.29
Nodes (8): main(), _parse_stats(), Path, Headless Locust smoke gate for CI.  Runs a short read-heavy scenario and fails, Return fail_ratio, p95_ms, failures, requests from Locust CSV stats., Path, Unit tests for Locust CI gate stats parsing (no live Locust run)., test_parse_stats_aggregated()

### Community 61 - "sso_views.py"
Cohesion: 0.33
Nodes (4): APIView, SsoCallbackView, SsoLoginView, SsoStatusView

### Community 62 - "CookieTokenRefreshView"
Cohesion: 0.22
Nodes (6): CookieAwareTokenRefreshSerializer, CookieTokenRefreshView, Cookie-aware JWT refresh — accepts refresh from body or httpOnly cookie., Refresh access tokens using body or the httpOnly refresh cookie., TokenRefreshSerializer, TokenRefreshView

### Community 63 - "Command"
Cohesion: 0.31
Nodes (4): Command, BaseCommand, Path, Create a PostgreSQL logical backup using pg_dump.

### Community 66 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, lint, preview, test, test:e2e, test:e2e:live (+1 more)

### Community 71 - "main.jsx"
Cohesion: 0.38
Nodes (4): App(), guard(), queryClient, initSentry()

### Community 73 - "Command"
Cohesion: 0.33
Nodes (3): Command, BaseCommand, Management command: report English/Arabic bilingual content completeness.  Usa

### Community 74 - "TenantsConfig"
Cohesion: 0.33
Nodes (3): AppConfig, TenantsConfig, Tenant signal handlers.  Subscription provisioning on organization creation li

### Community 81 - "package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 89 - "vercel.json"
Cohesion: 0.50
Nodes (3): buildCommand, outputDirectory, rewrites

### Community 196 - "upload_file"
Cohesion: 0.48
Nodes (6): get_signed_url(), get_supabase_client(), _local_media_url(), _save_local_file(), upload_file(), Client

## Knowledge Gaps
- **152 isolated node(s):** `Migration`, `Migration`, `Migration`, `Migration`, `Migration` (+147 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **77 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_current_organization()` connect `get_current_organization` to `accounts/views.py`, `log_activity`, `quizzes/views.py`, `Membership`, `OrganizationInvite`, `core/middleware.py`, `Subscription`, `Organization`, `notifications/views.py`, `enterprise_views.py`, `SmsMessage`, `billing/services.py`, `tutor/services.py`, `Article`, `grade_a_views.py`, `BaseBillingProvider`, `sms_views.py`, `MediaAssetSerializer`, `learning/views.py`, `apply_subscription_updated`, `ArticleSerializer`, `test_tutor_retrieval.py`, `tenants/permissions.py`, `get_membership`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `Membership` connect `Membership` to `accounts/views.py`, `log_activity`, `quizzes/views.py`, `get_current_organization`, `sso.py`, `forum/views.py`, `OrganizationInvite`, `Subscription`, `Organization`, `enterprise_views.py`, `conftest.py`, `SmsMessage`, `Notification`, `test_saas.py`, `Article`, `MediaAssetSerializer`, `learning/views.py`, `session.py`, `tenants/permissions.py`, `test_enterprise_gaps.py`, `test_sms.py`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `bind_client_to_org()` connect `bind_client_to_org` to `accounts/views.py`, `quizzes/views.py`, `forum/views.py`, `Membership`, `Subscription`, `conftest.py`, `Notification`, `tutor/services.py`, `Article`, `test_enterprise_gaps.py`, `test_api.py`, `test_sms.py`, `TestOrganizationInvites`, `TestTutorChat`, `TestUserRoleUpdate`, `TestMediaLibraryApi`, `TestSmsAlerts`, `TestPushAdmin`, `TestAuditLogs`, `TestInAppBroadcast`, `TestCertificateTask`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `Membership` (e.g. with `MembershipAdmin` and `OrganizationAdmin`) actually correct?**
  _`Membership` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 51 inferred relationships involving `Role` (e.g. with `Command` and `Command`) actually correct?**
  _`Role` has 51 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Migration`, `Migration`, `Migration` to the rest of the system?**
  _152 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `accounts/views.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05232605014915746 - nodes in this community are weakly interconnected._