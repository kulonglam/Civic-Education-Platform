# Graph Report - Civic Education Platform  (2026-08-21)

## Corpus Check
- 438 files · ~170,484 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2748 nodes · 6306 edges · 243 communities (167 shown, 76 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 337 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b8de06a8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- UserSerializer
- scim.py
- quizzes/views.py
- get_current_organization
- sso.py
- ui.jsx
- forum/views.py
- verification.py
- QuizTakePage.jsx
- log_activity
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
- tenants/views.py
- conftest.py
- TutorPage.jsx
- learning/serializers.py
- billing/services.py
- audit/services.py
- tutor/views.py
- test_saas.py
- dependencies
- test_medium_features.py
- enterprise_views.py
- integrations.py
- TenantModel
- devDependencies
- BaseBillingProvider
- sms_views.py
- django_db
- OrganizationInvite
- eslint
- fan_out.py
- sms_services.py
- TestForum
- apply_subscription_updated
- accounts/models.py
- services.js
- NotificationConsumer
- CivicUser
- Command
- test_deploy.py
- tutor/services.py
- test_tutor_retrieval.py
- compilerOptions
- Pre-launch checklist
- Membership
- sms_providers.py
- views/mfa.py
- Article
- test_tutor_providers.py
- Production environment checklist — integrations
- CiSmokeUser
- _parse_stats
- test_auth_flows.py
- TutorUnavailable
- Command
- TestAuth
- grade_a_views.py
- scripts
- learning/views.py
- TestOrganizationInvites
- notifications/models.py
- helpers.js
- Command
- main.jsx
- Command
- TenantsConfig
- views/__init__.py
- Load testing (Locust)
- Backend setup
- progress.py
- session.py
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
- TestOrgAnalytics
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
- user_management.py
- OrganizationSerializer
- log_security_event
- bump_session_epoch
- media_views.py
- TestLearningProgress
- Civic Education RSS API Reference
- learning/signals.py
- TestTutorChat
- Testing & CI
- urls/auth.py
- test_enterprise_gaps.py
- TestPushAdmin
- jwt.js
- MediaAsset
- Command
- 0009_learning_progress.py
- TestArticleI18n
- prompts.py
- password.py
- TestTenantIsolation
- tailwindcss
- @testing-library/jest-dom
- @testing-library/react
- notifications/admin.py
- RecordingProvider
- content_bundle
- EngagementConfig
- GamificationConfig
- TestBackfillAuditOrgs
- TenantMiddleware
- test_product_features.py
- UserManager
- TestMediaLibraryApi
- billing/signals.py
- globals
- @playwright/test
- start.sh
- vite
- 0006_userprofile_xp_points.py
- engagement/migrations/0001_initial.py
- gamification/migrations/0001_initial.py
- 0010_article_tutor_index_text_mediaasset_captions_url.py
- JWTCookieAuthentication
- core/serializers.py
- TestInAppBroadcast

## God Nodes (most connected - your core abstractions)
1. `bind_client_to_org()` - 110 edges
2. `get_current_organization()` - 94 edges
3. `log_activity()` - 78 edges
4. `Membership` - 67 edges
5. `extractError()` - 53 edges
6. `useAuth()` - 39 edges
7. `Article` - 37 edges
8. `Role` - 36 edges
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

## Communities (243 total, 76 thin omitted)

### Community 0 - "UserSerializer"
Cohesion: 0.20
Nodes (3): ProfileUpdateSerializer, UserSerializer, ProfileView

### Community 1 - "scim.py"
Cohesion: 0.16
Nodes (15): OrganizationScimToken, Bearer token for SCIM 2.0 provisioning integrations (hashed at rest)., authenticate_scim(), _group_to_scim(), APIView, SCIM 2.0 Groups — mapped to organization departments., ScimGroupDetailView, ScimGroupsView (+7 more)

### Community 2 - "quizzes/views.py"
Cohesion: 0.05
Nodes (50): AvatarUploadView, MyDataExportView, APIView, extend_schema, Self-service profile, avatar, data export and deactivation., Download the authenticated user's personal data (GDPR-style)., get_signed_url(), get_supabase_client() (+42 more)

### Community 3 - "get_current_organization"
Cohesion: 0.05
Nodes (48): IsOrgAnalyticsAdmin, BasePermission, Organization owner or admin (analytics plan checked in the view)., _attempts_queryset(), build_dashboard_summary(), build_institutional_report_pdf(), build_member_progress(), build_my_learning_summary() (+40 more)

### Community 4 - "sso.py"
Cohesion: 0.07
Nodes (47): build_authorize_url(), claims_from_tokens(), exchange_code_for_tokens(), _fetch_jwks(), fetch_oidc_metadata(), fetch_userinfo(), get_or_create_user_from_sso(), get_org_sso_config() (+39 more)

### Community 5 - "ui.jsx"
Cohesion: 0.10
Nodes (37): CertificatesPage, QuizzesPage, GamificationSummary(), Trophy(), Pagination(), Alert(), CardSkeleton(), ConfirmDialog() (+29 more)

### Community 6 - "forum/views.py"
Cohesion: 0.12
Nodes (19): DiscussionComment, DiscussionTopic, Meta, CommentCreateSerializer, DiscussionCommentSerializer, DiscussionTopicCreateSerializer, DiscussionTopicSerializer, Meta (+11 more)

### Community 7 - "verification.py"
Cohesion: 0.20
Nodes (10): AnonRateThrottle, PhoneVerifyConfirmSerializer, PhoneVerifyConfirmView, PhoneVerifySendView, APIView, extend_schema, Email and phone verification., ResendVerificationEmailView (+2 more)

### Community 8 - "QuizTakePage.jsx"
Cohesion: 0.18
Nodes (16): QuizTakePage, OfflineBanner(), useOnlineStatus(), api, getDb(), flushQuizQueue(), getQueuedQuizCount(), loadQuiz() (+8 more)

### Community 9 - "log_activity"
Cohesion: 0.18
Nodes (8): UserRoleUpdateSerializer, _get_managed_user(), extend_schema, Resolve a user visible in the current admin/moderator list., _client_meta(), log_activity(), ArticleViewSet, action

### Community 10 - "bind_client_to_org"
Cohesion: 0.13
Nodes (7): bind_client_to_org(), Authenticate and scope requests to ``org`` (creates membership if needed)., TestArticles, TestSmsAlerts, TestCertificateTask, django_db, TestUserRoleUpdate

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
Cohesion: 0.20
Nodes (14): get_billing_provider(), CheckoutSerializer, SubscriptionSerializer, ensure_subscription(), get_subscription(), Return the org subscription, creating a free-plan row if missing., BillingPortalView, CheckoutView (+6 more)

### Community 17 - "ArticleDetailPage.jsx"
Cohesion: 0.11
Nodes (28): ArticleEditorPage, MediaPlayer(), useDebouncedValue(), readingTime(), plainTextExcerpt(), renderMarkdown(), SANITIZE_OPTIONS, API_ORIGIN (+20 more)

### Community 18 - "test_grade_a_enterprise.py"
Cohesion: 0.10
Nodes (16): enable_mfa(), login_user(), Enroll a test user in TOTP MFA (privileged routes require this)., Log in via API, completing MFA when enrolled., django_db, Grade-A enterprise: sessions, SCIM, compliance, support, IP allowlist., TestAuditIntegrity, TestIpAllowlist (+8 more)

### Community 19 - "notifications/views.py"
Cohesion: 0.13
Nodes (18): BroadcastNotificationSerializer, WebPushSubscribeSerializer, Notification, WebPushSubscription, cleanup_push_subscriptions(), push_subscription_stats(), BroadcastNotificationView, Meta (+10 more)

### Community 20 - "tenants/views.py"
Cohesion: 0.13
Nodes (24): check_quota(), Raise ``QuotaExceeded`` if creating one more ``resource`` would exceed the plan., Public platform branding strings., InvitePreviewSerializer, MemberInviteSerializer, MemberRoleUpdateSerializer, MembershipSerializer, OrganizationInviteSerializer (+16 more)

### Community 21 - "conftest.py"
Cohesion: 0.15
Nodes (15): Command, BaseCommand, Role, admin_user(), api_client(), category(), citizen_user(), editor_user() (+7 more)

### Community 22 - "TutorPage.jsx"
Cohesion: 0.14
Nodes (22): TutorPage, LanguageSwitcher(), applyDirection(), initial, DEFAULT_LANGUAGE, normalizeLanguage(), RTL_LANGUAGES, sanitizeStoredLanguage() (+14 more)

### Community 23 - "learning/serializers.py"
Cohesion: 0.10
Nodes (8): ArticleSerializer, _can_publish_directly(), MediaAssetSerializer, MediaAssetSummarySerializer, Meta, Compact nested representation for articles., validate_http_url(), TestMediaHttpUrlValidation

### Community 24 - "billing/services.py"
Cohesion: 0.19
Nodes (14): extend_schema, AnalyticsNotAvailable, count_usage(), get_active_plan(), invalidate_quota_cache(), plan_has_analytics(), plan_has_sms(), plan_has_sso() (+6 more)

### Community 25 - "audit/services.py"
Cohesion: 0.14
Nodes (13): Command, BaseCommand, ActivityLog, Meta, ActivityLogSerializer, Meta, compute_integrity_hash(), Verify hash-chain integrity for recent activity logs. (+5 more)

### Community 26 - "tutor/views.py"
Cohesion: 0.13
Nodes (22): ChatRequestSerializer, ChatResponseSerializer, TutorMessageSerializer, TutorSessionSerializer, TutorSessionSummarySerializer, TutorSourceSerializer, TutorUsageSerializer, get_tutor_service() (+14 more)

### Community 27 - "test_saas.py"
Cohesion: 0.18
Nodes (5): django_db, TestBilling, TestMyOrganizations, TestOrganizationRegistration, TestQuotas

### Community 28 - "dependencies"
Cohesion: 0.08
Nodes (25): axios, dompurify, dependencies, axios, dompurify, i18next, i18next-browser-languagedetector, idb (+17 more)

### Community 29 - "test_medium_features.py"
Cohesion: 0.07
Nodes (18): register, TutorChatAdmin, get_chat_session_history(), list_chat_sessions(), Read access to persisted tutor conversations., Return ordered messages for a persisted session owned by the user., Summarize recent tutor conversations persisted for the user., Meta (+10 more)

### Community 30 - "enterprise_views.py"
Cohesion: 0.08
Nodes (25): require_sso(), BulkMemberImportView, DepartmentDetailView, DepartmentListCreateView, _org_support_snapshot(), OrganizationSsoConfigView, PlatformOrganizationDetailView, PlatformOrganizationListView (+17 more)

### Community 31 - "integrations.py"
Cohesion: 0.08
Nodes (36): build_integrations_report(), check_cache(), check_celery(), check_database(), check_email(), check_oidc(), check_pypdf(), check_sentry() (+28 more)

### Community 32 - "TenantModel"
Cohesion: 0.05
Nodes (46): get_preferred_language(), Resolve API content language to ``en`` or ``ar`` only., Campaign, Meta, Petition, PetitionSignature, Poll, PollOption (+38 more)

### Community 33 - "devDependencies"
Cohesion: 0.09
Nodes (23): autoprefixer, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, devDependencies, autoprefixer, @eslint/js, eslint-plugin-react-hooks (+15 more)

### Community 34 - "BaseBillingProvider"
Cohesion: 0.12
Nodes (6): BaseBillingProvider, CheckoutResult, DummyBillingProvider, Pluggable billing providers. The ``dummy`` provider requires no external…, No-op provider for local dev/tests; activates plans instantly., StripeBillingProvider

### Community 35 - "sms_views.py"
Cohesion: 0.15
Nodes (21): require_sms(), SmsMessage, BroadcastSmsSerializer, Meta, SendSmsSerializer, SmsMessageSerializer, deliver_sms(), org_member_phones() (+13 more)

### Community 36 - "django_db"
Cohesion: 0.17
Nodes (5): django_db, TestEngagement, TestGamification, TestMediaCaptions, TestTutorStream

### Community 37 - "OrganizationInvite"
Cohesion: 0.28
Nodes (6): MembershipAdmin, OrganizationAdmin, OrganizationInviteAdmin, register, OrganizationInvite, Pending email invitation to join an organization.

### Community 39 - "fan_out.py"
Cohesion: 0.15
Nodes (15): Push a notification dict to all WebSocket connections for ``user_pk``. Call…, send_notification_to_user(), _get_or_create_prefs(), notify_user(), Unified notification fan-out. Call :func:`notify_user` to deliver a…, Create an in-app Notification and fan-out to configured channels. Returns the…, Fire-and-forget async send to the user's WebSocket group., _sms_push() (+7 more)

### Community 40 - "sms_services.py"
Cohesion: 0.39
Nodes (11): PhoneOTP, normalize_phone(), Normalize to E.164 for South Sudan (+211)., create_sms_log(), issue_phone_otp(), queue_sms_to_phone(), send_password_reset_otp(), send_phone_verify_otp() (+3 more)

### Community 41 - "TestForum"
Cohesion: 0.20
Nodes (4): django_db, TestAnalytics, TestForum, TestQuizzes

### Community 42 - "apply_subscription_updated"
Cohesion: 0.19
Nodes (11): apply_checkout_completed(), _apply_plan_code(), apply_subscription_deleted(), apply_subscription_updated(), plan_code_for_stripe_price(), Sync subscription after Stripe Checkout completes., Sync plan/status when Stripe subscription changes., Downgrade to the free plan when a paid subscription ends. (+3 more)

### Community 43 - "accounts/models.py"
Cohesion: 0.23
Nodes (8): AbstractBaseUser, EmailVerificationToken, Meta, User, UserProfile, ensure_profile(), receiver, PermissionsMixin

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
Cohesion: 0.10
Nodes (23): CoreConfig, AppConfig, production_security_checks(), register, Validate settings required for a safe production deployment., Helpers for building Django ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS lists., Split comma-separated host strings and return de-duplicated hosts., Return the Render service hostname from platform-injected env vars. (+15 more)

### Community 49 - "tutor/services.py"
Cohesion: 0.13
Nodes (26): get_user_organization(), Return the user's primary organization (first membership), or None., _daily_cache_key(), enforce_budget(), get_daily_limit(), get_daily_usage(), increment_daily_usage(), Daily message quota for the AI tutor. Usage is counted in Redis for speed and… (+18 more)

### Community 50 - "test_tutor_retrieval.py"
Cohesion: 0.09
Nodes (30): build_tutor_index_text(), Build and maintain pre-indexed tutor search text on articles., Combine article body and PDF attachment text for tutor retrieval., set_current_organization(), extract_pdf_text(), fetch_attachment_bytes(), get_attachment_text(), _local_media_path() (+22 more)

### Community 51 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, baseUrl, checkJs, jsx, module, moduleResolution, target, types (+4 more)

### Community 52 - "Pre-launch checklist"
Cohesion: 0.10
Nodes (20): 10. Ongoing operations, 11. Organization invites, 12. Error monitoring (Sentry), 13. Database backups, 14. E2E testing, 1. Domain and TLS, 2. Backend secrets, 3. Database (+12 more)

### Community 53 - "Membership"
Cohesion: 0.10
Nodes (20): Resolves the current tenant for each request. Resolution order: 1. ``X-Tenant-…, Department, Membership, Meta, Organization, OrganizationSsoConfig, A tenant. All customer data is isolated per organization., Organizational unit within a tenant (ministry division, county office, etc.). (+12 more)

### Community 54 - "sms_providers.py"
Cohesion: 0.29
Nodes (6): AfricasTalkingSmsProvider, BaseSmsProvider, DummySmsProvider, get_sms_provider(), Log SMS in development; always succeeds., SmsSendResult

### Community 55 - "views/mfa.py"
Cohesion: 0.11
Nodes (26): consume_mfa_challenge(), generate_totp_secret(), issue_mfa_challenge(), provisioning_uri(), TOTP multi-factor authentication for privileged accounts., Platform admins and organization owners/admins must use MFA when org requires…, totp_for_secret(), user_has_mfa_enabled() (+18 more)

### Community 56 - "Article"
Cohesion: 0.13
Nodes (13): Article, Category, global_search(), Unified keyword search across published learning content and forum topics., Scope search to the request tenant, defaulting to the public workspace., _resolve_search_organization(), GlobalSearchView, APIView (+5 more)

### Community 57 - "test_tutor_providers.py"
Cohesion: 0.11
Nodes (15): _anthropic_configured(), BaseTutorProvider, get_tutor_provider(), _last_user_message(), _openai_configured(), Pluggable AI providers for the tutor. Mirrors ``apps/billing/providers.py``: a…, Resolve the active provider, degrading to the stub when credentials are missing., Offline provider used when no AI credentials are configured. (+7 more)

### Community 58 - "Production environment checklist — integrations"
Cohesion: 0.06
Nodes (35): 10. Compliance / monitoring gates (production), 1. Celery + Redis (required), 2. Stripe billing (required for paid SaaS), 2b. No Stripe / unsupported country (e.g. Uganda), 3. SMS — Africa's Talking (optional), 4. Web push — VAPID (optional), 5. AI tutor (optional), 6. Enterprise SSO — OpenID Connect (optional) (+27 more)

### Community 59 - "CiSmokeUser"
Cohesion: 0.23
Nodes (4): CiSmokeUser, HttpUser, task, Lightweight Locust scenario for CI — avoids mass registration throttling.

### Community 60 - "_parse_stats"
Cohesion: 0.29
Nodes (8): main(), _parse_stats(), Path, Headless Locust smoke gate for CI. Runs a short read-heavy scenario and fails…, Return fail_ratio, p95_ms, failures, requests from Locust CSV stats., Path, Unit tests for Locust CI gate stats parsing (no live Locust run)., test_parse_stats_aggregated()

### Community 61 - "test_auth_flows.py"
Cohesion: 0.12
Nodes (6): django_db, TestEmailVerification, TestLogoutBlacklist, TestPasswordReset, TestSuspension, TestTokenRefresh

### Community 62 - "TutorUnavailable"
Cohesion: 0.18
Nodes (6): APIException, TutorUnavailable, AnthropicTutorProvider, OpenAICompatibleTutorProvider, Any OpenAI-compatible endpoint: OpenAI, Ollama, OpenRouter, Groq, Together., FailingProvider

### Community 63 - "Command"
Cohesion: 0.31
Nodes (4): Command, BaseCommand, Path, Create a PostgreSQL logical backup using pg_dump.

### Community 64 - "TestAuth"
Cohesion: 0.25
Nodes (3): django_db, TestAuth, TestHealthCheck

### Community 65 - "grade_a_views.py"
Cohesion: 0.10
Nodes (18): AuditIntegrityVerifyView, ComplianceEvidencePackView, _hash_token(), PlatformSupportCaseListView, PlatformSupportCaseUpdateView, APIView, Grade-A enterprise APIs: SCIM tokens, compliance pack, support cases, SLO., Download a compliance evidence pack for audits (ISO/SOC-style evidence). (+10 more)

### Community 66 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, lint, preview, test, test:e2e, test:e2e:live (+1 more)

### Community 67 - "learning/views.py"
Cohesion: 0.11
Nodes (14): CategorySerializer, _can_see_unpublished(), CategoryViewSet, CanDeleteOrgContent, get_membership(), IsOrgContentEditor, IsOrgForumModerator, IsOrgMember (+6 more)

### Community 69 - "notifications/models.py"
Cohesion: 0.11
Nodes (9): notifications(), django_db, fixture, TestNotifications, free_plan(), pro_plan(), django_db, fixture (+1 more)

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

### Community 75 - "views/__init__.py"
Cohesion: 0.18
Nodes (11): EmailTokenObtainPairView, LoginView, LogoutView, APIView, Registration, login and logout., RegisterView, Account views. Split into cohesive submodules; every public view is re-exported…, shared_task (+3 more)

### Community 76 - "Load testing (Locust)"
Cohesion: 0.17
Nodes (12): Background tasks (Celery + Redis), CI load-test gate, CI load-test gate, Eager fallback (dev / test), Getting meaningful numbers, Headless ramp toward the SRS concurrency target, Institutional scale notes (10k concurrent), Load testing (Locust) (+4 more)

### Community 77 - "Backend setup"
Cohesion: 0.15
Nodes (13): AI tutor (RAG), API reference, Backend setup, Background tasks (Celery), Civic Education RSS, Default accounts (after `seed_data`), Deployment (Render), Load testing (+5 more)

### Community 78 - "progress.py"
Cohesion: 0.22
Nodes (11): award_xp(), ArticleProgress, MediaProgress, Meta, Record and query learner progress on articles and media., record_article_progress(), record_media_progress(), _resolve_organization() (+3 more)

### Community 79 - "session.py"
Cohesion: 0.23
Nodes (10): Cookie-aware JWT authentication. Checks httpOnly cookies first (preferred, more…, check_session_idle(), get_session_epoch(), is_privileged_user(), Server-side session controls: idle timeout and epoch-based revocation., Privileged sessions enforce idle timeout (platform staff or org admins)., Raise AuthenticationFailed if a privileged user has been idle too long., session_idle_seconds() (+2 more)

### Community 80 - "Subscription"
Cohesion: 0.16
Nodes (11): PlanAdmin, register, SubscriptionAdmin, Meta, Plan, A subscription tier with pricing and per-tenant quotas., Subscription, Meta (+3 more)

### Community 81 - "package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 83 - "Civic Education RSS — Frontend"
Cohesion: 0.22
Nodes (8): Civic Education RSS — Frontend, Deployment, Environment variables, Features, Local setup, Project structure, Requirements, Scripts

### Community 86 - "accounts/serializers.py"
Cohesion: 0.26
Nodes (9): Meta, RegisterSerializer, RoleSerializer, UserProfileSerializer, accept_organization_invite(), get_valid_invite(), join_public_organization(), Accept a pending invite and return the new membership. (+1 more)

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

### Community 148 - "user_management.py"
Cohesion: 0.15
Nodes (16): APIView, Moderator and admin actions on other users., SuspendUserView, UnsuspendUserView, UpdateUserRoleView, UserListView, IsAdmin, IsCitizenOrAbove (+8 more)

### Community 149 - "OrganizationSerializer"
Cohesion: 0.32
Nodes (4): normalize_primary_color(), Return green default when ``color`` is a legacy blue brand value., OrganizationSerializer, CurrentOrganizationView

### Community 150 - "log_security_event"
Cohesion: 0.31
Nodes (7): custom_exception_handler(), Log permission denials and MFA setup blocks as security events., _client_ip(), log_security_event(), Any, Structured security event logging for monitoring and incident response., Emit a structured security log entry and persist for platform admin review.

### Community 192 - "bump_session_epoch"
Cohesion: 0.19
Nodes (8): bump_session_epoch(), Invalidate all outstanding JWTs for this user by advancing session_epoch., extend_schema, DeactivateAccountView, Soft-deactivate the authenticated account., APIView, SCIM User resource: get / patch / deactivate., ScimUserDetailView

### Community 196 - "media_views.py"
Cohesion: 0.15
Nodes (11): _can_see_unpublished(), MediaAssetFilter, MediaAssetViewSet, MediaAudioUploadView, MediaVideoUploadView, Meta, action, APIView (+3 more)

### Community 198 - "Civic Education RSS API Reference"
Cohesion: 0.29
Nodes (7): Civic Education RSS API Reference, Conventions, Endpoint index, Gamification & engagement, Ops commands, Related docs, Tutor API (summary)

### Community 199 - "learning/signals.py"
Cohesion: 0.26
Nodes (9): maintain_tutor_index(), notify_on_publish(), receiver, track_attachment_change(), notify_all_users(), Fan out a notification to all active users via a background task. When…, _cache_key(), invalidate_attachment_text_cache() (+1 more)

### Community 200 - "TestTutorChat"
Cohesion: 0.18
Nodes (3): django_db, TestTutorAdminUsage, TestTutorChat

### Community 201 - "Testing & CI"
Cohesion: 0.20
Nodes (10): Backend tests, CI pipeline (`.github/workflows/ci.yml`), E2E tests (Playwright), Environment variables (live e2e), Frontend unit tests (Vitest), Live backend (`e2e-live` CI job), Mocked API (default — `frontend` CI job), Ops smoke (loadtest job) (+2 more)

### Community 202 - "urls/auth.py"
Cohesion: 0.15
Nodes (10): APIView, SsoCallbackView, SsoLoginView, SsoStatusView, CookieAwareTokenRefreshSerializer, CookieTokenRefreshView, Cookie-aware JWT refresh — accepts refresh from body or httpOnly cookie., Refresh access tokens using body or the httpOnly refresh cookie. (+2 more)

### Community 203 - "test_enterprise_gaps.py"
Cohesion: 0.14
Nodes (8): Meta, Persisted security events for platform-admin monitoring dashboards., SecurityEvent, django_db, Tests for remaining enterprise gaps: org RBAC, content packs, platform support., TestContentPacks, TestOrgRoleRBAC, TestPlatformSupportAndSecurity

### Community 204 - "TestPushAdmin"
Cohesion: 0.24
Nodes (4): django_db, TestPushAdmin, TestSsoStatus, override_settings

### Community 206 - "MediaAsset"
Cohesion: 0.31
Nodes (7): MediaAsset, django_db, Coverage-oriented tests for media–article linking and MediaAsset helpers., test_article_can_attach_audio_and_video(), test_article_rejects_wrong_media_type(), test_media_asset_playback_url_external(), test_media_asset_playback_url_prefers_upload()

### Community 209 - "TestArticleI18n"
Cohesion: 0.18
Nodes (4): django_db, TestArticleI18n, TestQuizI18n, TestQuizOptionsI18n

### Community 210 - "prompts.py"
Cohesion: 0.31
Nodes (7): normalize_language(), Shared application constants., Return ``en`` or ``ar``; any other value maps to ``en``., build_system_prompt(), System prompt construction for the AI tutor., _user_language(), format_retrieved_context()

### Community 211 - "password.py"
Cohesion: 0.13
Nodes (13): PasswordResetConfirmSerializer, PasswordResetOtpConfirmSerializer, PasswordResetOtpRequestSerializer, PasswordResetRequestSerializer, ChangePasswordView, PasswordResetConfirmView, PasswordResetOtpConfirmView, PasswordResetOtpRequestView (+5 more)

### Community 212 - "TestTenantIsolation"
Cohesion: 0.25
Nodes (4): An article cannot reference a category that belongs to a different org., Org switcher: header selects another org the user belongs to., The tenant middleware must ignore X-Tenant-Slug for orgs the user doesn't…, TestTenantIsolation

### Community 216 - "notifications/admin.py"
Cohesion: 0.40
Nodes (4): register, SmsMessageAdmin, WebPushSubscriptionAdmin, display

### Community 217 - "RecordingProvider"
Cohesion: 0.29
Nodes (4): django_db, Honors the (text, 0) deltas then ('', total_tokens) terminal contract., RecordingProvider, TestServiceHonorsProviderContract

### Community 218 - "content_bundle"
Cohesion: 0.29
Nodes (6): api_view, content_bundle(), ContentBundleThrottle, UserRateThrottle, Download a full offline study pack for the current organisation. Returns all…, permission_classes

### Community 223 - "test_product_features.py"
Cohesion: 0.16
Nodes (6): django_db, TestAuditLogs, TestPhoneVerification, TestResendVerificationEmail, TestUnsuspendUser, TestWebPushSubscribe

### Community 226 - "billing/signals.py"
Cohesion: 0.25
Nodes (6): BillingConfig, AppConfig, get_default_plan(), create_default_subscription(), receiver, Every new organization starts on the default (free) plan.

### Community 240 - "JWTCookieAuthentication"
Cohesion: 0.50
Nodes (3): JWTCookieAuthentication, Authenticate via httpOnly cookie if present; fall back to Bearer header., JWTAuthentication

### Community 241 - "core/serializers.py"
Cohesion: 0.40
Nodes (4): DetailSerializer, MessageSerializer, Generic ``{"detail": "..."}`` response body., Generic ``{"message": "..."}`` response body.

## Knowledge Gaps
- **267 isolated node(s):** `Migration`, `Migration`, `Migration`, `Migration`, `Migration` (+262 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **76 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_current_organization()` connect `get_current_organization` to `quizzes/views.py`, `log_activity`, `core/middleware.py`, `billing/views.py`, `notifications/views.py`, `user_management.py`, `tenants/views.py`, `OrganizationSerializer`, `learning/serializers.py`, `audit/services.py`, `enterprise_views.py`, `TenantModel`, `sms_views.py`, `sms_services.py`, `tutor/services.py`, `Membership`, `Article`, `grade_a_views.py`, `learning/views.py`, `media_views.py`, `progress.py`, `prompts.py`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `log_activity()` connect `log_activity` to `scim.py`, `quizzes/views.py`, `get_current_organization`, `forum/views.py`, `verification.py`, `test_grade_a_enterprise.py`, `user_management.py`, `tenants/views.py`, `OrganizationSerializer`, `audit/services.py`, `enterprise_views.py`, `views/mfa.py`, `bump_session_epoch`, `grade_a_views.py`, `learning/views.py`, `media_views.py`, `urls/auth.py`, `views/__init__.py`, `password.py`, `TestBackfillAuditOrgs`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `bind_client_to_org()` connect `bind_client_to_org` to `quizzes/views.py`, `forum/views.py`, `test_grade_a_enterprise.py`, `conftest.py`, `learning/serializers.py`, `test_medium_features.py`, `integrations.py`, `TenantModel`, `django_db`, `TestForum`, `Membership`, `views/mfa.py`, `Article`, `TestOrganizationInvites`, `TestLearningProgress`, `notifications/models.py`, `TestTutorChat`, `test_enterprise_gaps.py`, `TestPushAdmin`, `progress.py`, `MediaAsset`, `Subscription`, `TestArticleI18n`, `TestTopicModeration`, `test_product_features.py`, `TestMediaLibraryApi`, `TestOrgAnalytics`, `TestInAppBroadcast`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `Membership` (e.g. with `TenantMiddleware` and `CanDeleteOrgContent`) actually correct?**
  _`Membership` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Migration`, `Migration`, `Migration` to the rest of the system?**
  _267 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `quizzes/views.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05493827160493827 - nodes in this community are weakly interconnected._
- **Should `get_current_organization` be split into smaller, more focused modules?**
  _Cohesion score 0.05128205128205128 - nodes in this community are weakly interconnected._