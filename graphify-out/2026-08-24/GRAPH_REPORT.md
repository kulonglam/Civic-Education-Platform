# Graph Report - Civic Education Platform  (2026-08-24)

## Corpus Check
- 445 files · ~172,477 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2818 nodes · 6461 edges · 246 communities (167 shown, 79 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 339 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `77d746e4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- UserSerializer
- scim.py
- quizzes/views.py
- analytics/views.py
- Organization
- ui.jsx
- forum/views.py
- urls/auth.py
- QuizTakePage.jsx
- ArticleViewSet
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
- ActivityLog
- tutor/views.py
- test_saas.py
- dependencies
- TutorChat
- get_current_organization
- integrations.py
- engagement/views.py
- devDependencies
- BaseBillingProvider
- sms_views.py
- django_db
- translation.py
- eslint
- fan_out.py
- test_article_translation.py
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
- create_organization_with_owner
- sms_services.py
- views/mfa.py
- tenants/models.py
- test_tutor_providers.py
- Production environment checklist — integrations
- CiSmokeUser
- _parse_stats
- TestEmailVerification
- TutorUnavailable
- Command
- TestAuth
- grade_a_views.py
- scripts
- tenants/permissions.py
- TestOrganizationInvites
- TestNotifications
- helpers.js
- Command
- main.jsx
- Command
- TenantsConfig
- views/__init__.py
- Load testing (Locust)
- Backend setup
- apply_article_translation
- session.py
- Subscription
- package.json
- AccountsConfig
- Civic Education RSS — Frontend
- LearningConfig
- 0003_migrate_primary_color_to_green.py
- enable_mfa
- DeactivateAccountView
- TestTopicModeration
- vercel.json
- AnalyticsConfig
- AuditConfig
- ForumConfig
- NotificationsConfig
- QuizzesConfig
- TutorConfig
- Constitution & controlled documents
- StubTutorProvider
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
- TestGlobalSearch
- log_security_event
- bump_session_epoch
- _upload_media_file
- TestLearningProgress
- Civic Education RSS API Reference
- learning/signals.py
- TestTutorChat
- Testing & CI
- TestSmsAlerts
- TestContentPacks
- TestUserRoleUpdate
- jwt.js
- GlobalSearchView
- backfill_audit_orgs.py
- 0009_learning_progress.py
- TestPasswordReset
- prompts.py
- accounts/serializers.py
- test_org_analytics.py
- tailwindcss
- @testing-library/jest-dom
- @testing-library/react
- Notification
- BaseTutorProvider
- 1. Celery + Redis (required)
- EngagementConfig
- GamificationConfig
- log_activity
- TenantMiddleware
- test_product_features.py
- UserManager
- TestMediaLibraryApi
- 5. AI tutor (optional)
- globals
- @playwright/test
- start.sh
- Command
- 0006_userprofile_xp_points.py
- engagement/migrations/0001_initial.py
- gamification/migrations/0001_initial.py
- 0010_article_tutor_index_text_mediaasset_captions_url.py
- TestCitizenRegistration
- core/serializers.py
- 0011_article_translation.py
- @vitest/coverage-v8

## God Nodes (most connected - your core abstractions)
1. `bind_client_to_org()` - 110 edges
2. `get_current_organization()` - 94 edges
3. `log_activity()` - 78 edges
4. `Membership` - 67 edges
5. `extractError()` - 53 edges
6. `Article` - 43 edges
7. `useAuth()` - 39 edges
8. `Role` - 36 edges
9. `Organization` - 35 edges
10. `TenantModel` - 31 edges

## Surprising Connections (you probably didn't know these)
- `Command` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/management/commands/demote_legacy_org_admins.py → backend/apps/accounts/models.py
- `Command` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/management/commands/seed_data.py → backend/apps/accounts/models.py
- `RegisterSerializer` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/serializers.py → backend/apps/accounts/models.py
- `RoleSerializer` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/serializers.py → backend/apps/accounts/models.py
- `UserRoleUpdateSerializer` --uses--> `Role`  [INFERRED]
  backend/apps/accounts/serializers.py → backend/apps/accounts/models.py

## Import Cycles
- None detected.

## Communities (246 total, 79 thin omitted)

### Community 0 - "UserSerializer"
Cohesion: 0.14
Nodes (7): Meta, ProfileUpdateSerializer, RegisterSerializer, RoleSerializer, UserProfileSerializer, UserSerializer, ProfileView

### Community 1 - "scim.py"
Cohesion: 0.16
Nodes (15): OrganizationScimToken, Bearer token for SCIM 2.0 provisioning integrations (hashed at rest)., authenticate_scim(), _group_to_scim(), APIView, SCIM 2.0 Groups — mapped to organization departments., ScimGroupDetailView, ScimGroupsView (+7 more)

### Community 2 - "quizzes/views.py"
Cohesion: 0.06
Nodes (43): Self-service profile, avatar, data export and deactivation., get_signed_url(), get_supabase_client(), _local_media_url(), _save_local_file(), upload_bytesio(), upload_file(), Certificate (+35 more)

### Community 3 - "analytics/views.py"
Cohesion: 0.09
Nodes (33): IsOrgAnalyticsAdmin, BasePermission, Organization owner or admin (analytics plan checked in the view)., _attempts_queryset(), build_dashboard_summary(), build_institutional_report_pdf(), build_member_progress(), build_my_learning_summary() (+25 more)

### Community 4 - "Organization"
Cohesion: 0.06
Nodes (53): build_authorize_url(), claims_from_tokens(), exchange_code_for_tokens(), _fetch_jwks(), fetch_oidc_metadata(), fetch_userinfo(), get_or_create_user_from_sso(), get_org_sso_config() (+45 more)

### Community 5 - "ui.jsx"
Cohesion: 0.10
Nodes (37): CertificatesPage, QuizzesPage, GamificationSummary(), Trophy(), Pagination(), Alert(), CardSkeleton(), ConfirmDialog() (+29 more)

### Community 6 - "forum/views.py"
Cohesion: 0.13
Nodes (19): DiscussionComment, DiscussionTopic, Meta, CommentCreateSerializer, DiscussionCommentSerializer, DiscussionTopicCreateSerializer, DiscussionTopicSerializer, Meta (+11 more)

### Community 7 - "urls/auth.py"
Cohesion: 0.10
Nodes (17): PhoneVerifyConfirmSerializer, CookieAwareTokenRefreshSerializer, CookieTokenRefreshView, Cookie-aware JWT refresh — accepts refresh from body or httpOnly cookie., Refresh access tokens using body or the httpOnly refresh cookie., PhoneVerifyConfirmView, PhoneVerifySendView, APIView (+9 more)

### Community 8 - "QuizTakePage.jsx"
Cohesion: 0.18
Nodes (16): QuizTakePage, OfflineBanner(), useOnlineStatus(), api, getDb(), flushQuizQueue(), getQueuedQuizCount(), loadQuiz() (+8 more)

### Community 9 - "ArticleViewSet"
Cohesion: 0.13
Nodes (9): ArticleAttachmentUploadView, ArticleImageUploadView, ArticleViewSet, _can_see_unpublished(), action, APIView, extend_schema, Upload a PDF or document attachment for an article (e.g. full constitution… (+1 more)

### Community 10 - "bind_client_to_org"
Cohesion: 0.13
Nodes (7): bind_client_to_org(), Authenticate and scope requests to ``org`` (creates membership if needed)., TestArticles, django_db, TestOrgAnalytics, TestInAppBroadcast, TestCertificateTask

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
Cohesion: 0.21
Nodes (13): get_billing_provider(), CheckoutSerializer, Meta, PlanSerializer, SubscriptionSerializer, BillingPortalView, CheckoutView, CurrentSubscriptionView (+5 more)

### Community 17 - "ArticleDetailPage.jsx"
Cohesion: 0.11
Nodes (28): ArticleEditorPage, MediaPlayer(), useDebouncedValue(), readingTime(), plainTextExcerpt(), renderMarkdown(), SANITIZE_OPTIONS, API_ORIGIN (+20 more)

### Community 18 - "test_grade_a_enterprise.py"
Cohesion: 0.18
Nodes (10): login_user(), Log in via API, completing MFA when enrolled., django_db, Grade-A enterprise: sessions, SCIM, compliance, support, IP allowlist., TestAuditIntegrity, TestIpAllowlist, TestScimProvisioning, TestSessionControls (+2 more)

### Community 19 - "notifications/views.py"
Cohesion: 0.14
Nodes (17): BroadcastNotificationSerializer, WebPushSubscribeSerializer, WebPushSubscription, cleanup_push_subscriptions(), push_subscription_stats(), BroadcastNotificationView, Meta, NotificationListView (+9 more)

### Community 20 - "Membership"
Cohesion: 0.07
Nodes (47): check_quota(), Raise ``QuotaExceeded`` if creating one more ``resource`` would exceed the plan., normalize_primary_color(), Return green default when ``color`` is a legacy blue brand value., Department, Membership, Meta, OrganizationInvite (+39 more)

### Community 21 - "conftest.py"
Cohesion: 0.25
Nodes (13): Platform admins and organization owners/admins must use MFA when org requires…, user_requires_mfa(), Role, admin_user(), api_client(), category(), citizen_user(), editor_user() (+5 more)

### Community 22 - "TutorPage.jsx"
Cohesion: 0.14
Nodes (22): TutorPage, LanguageSwitcher(), applyDirection(), initial, DEFAULT_LANGUAGE, normalizeLanguage(), RTL_LANGUAGES, sanitizeStoredLanguage() (+14 more)

### Community 23 - "ArticleSerializer"
Cohesion: 0.09
Nodes (9): ArticleSerializer, _can_publish_directly(), MediaAssetSerializer, MediaAssetSummarySerializer, Meta, Compact nested representation for articles., validate_http_url(), django_db (+1 more)

### Community 24 - "billing/services.py"
Cohesion: 0.12
Nodes (23): APIView, extend_schema, SsoCallbackView, SsoLoginView, SsoStatusView, AnalyticsNotAvailable, count_usage(), ensure_subscription() (+15 more)

### Community 25 - "ActivityLog"
Cohesion: 0.17
Nodes (10): Command, BaseCommand, ActivityLog, Meta, ActivityLogSerializer, Meta, ActivityLogExportView, ActivityLogListView (+2 more)

### Community 26 - "tutor/views.py"
Cohesion: 0.13
Nodes (22): ChatRequestSerializer, ChatResponseSerializer, TutorMessageSerializer, TutorSessionSerializer, TutorSessionSummarySerializer, TutorSourceSerializer, TutorUsageSerializer, get_tutor_service() (+14 more)

### Community 27 - "test_saas.py"
Cohesion: 0.11
Nodes (9): django_db, An article cannot reference a category that belongs to a different org., Org switcher: header selects another org the user belongs to., The tenant middleware must ignore X-Tenant-Slug for orgs the user doesn't…, TestBilling, TestMyOrganizations, TestOrganizationRegistration, TestQuotas (+1 more)

### Community 28 - "dependencies"
Cohesion: 0.08
Nodes (25): axios, dompurify, dependencies, axios, dompurify, i18next, i18next-browser-languagedetector, idb (+17 more)

### Community 29 - "TutorChat"
Cohesion: 0.13
Nodes (13): register, TutorChatAdmin, get_chat_session_history(), list_chat_sessions(), Read access to persisted tutor conversations., Return ordered messages for a persisted session owned by the user., Summarize recent tutor conversations persisted for the user., Meta (+5 more)

### Community 30 - "get_current_organization"
Cohesion: 0.06
Nodes (23): get_current_organization(), BulkMemberImportView, DepartmentDetailView, DepartmentListCreateView, _org_support_snapshot(), OrganizationSsoConfigView, PlatformOrganizationDetailView, PlatformOrganizationListView (+15 more)

### Community 31 - "integrations.py"
Cohesion: 0.08
Nodes (36): build_integrations_report(), check_cache(), check_celery(), check_database(), check_email(), check_oidc(), check_pypdf(), check_sentry() (+28 more)

### Community 32 - "engagement/views.py"
Cohesion: 0.06
Nodes (40): get_preferred_language(), Resolve API content language to ``en`` or ``ar`` only., Campaign, Meta, Petition, PetitionSignature, Poll, PollOption (+32 more)

### Community 33 - "devDependencies"
Cohesion: 0.09
Nodes (23): autoprefixer, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, devDependencies, autoprefixer, @eslint/js, eslint-plugin-react-hooks (+15 more)

### Community 34 - "BaseBillingProvider"
Cohesion: 0.12
Nodes (6): BaseBillingProvider, CheckoutResult, DummyBillingProvider, Pluggable billing providers. The ``dummy`` provider requires no external…, No-op provider for local dev/tests; activates plans instantly., StripeBillingProvider

### Community 35 - "sms_views.py"
Cohesion: 0.19
Nodes (14): require_sms(), BroadcastSmsSerializer, Meta, SendSmsSerializer, SmsMessageSerializer, BroadcastSmsView, PlatformBroadcastSmsView, APIView (+6 more)

### Community 36 - "django_db"
Cohesion: 0.17
Nodes (5): django_db, TestEngagement, TestGamification, TestMediaCaptions, TestTutorStream

### Community 37 - "translation.py"
Cohesion: 0.12
Nodes (16): Command, BaseCommand, Enqueue automatic translation for articles missing English or Arabic., shared_task, Fill the missing English or Arabic side of an article., translate_article_task(), _build_updates(), _is_blank() (+8 more)

### Community 39 - "fan_out.py"
Cohesion: 0.16
Nodes (14): _get_or_create_prefs(), notify_user(), Unified notification fan-out. Call :func:`notify_user` to deliver a…, Create an in-app Notification and fan-out to configured channels. Returns the…, Fire-and-forget async send to the user's WebSocket group., _sms_push(), _web_push(), _ws_push() (+6 more)

### Community 40 - "test_article_translation.py"
Cohesion: 0.13
Nodes (13): chunk_markdown(), detect_language(), Return ``ar`` when Arabic letters outnumber Latin letters, else ``en``., Split on blank-line paragraph boundaries, keeping chunks under max_chars., english_article(), django_db, fixture, TestChunkMarkdown (+5 more)

### Community 41 - "TestForum"
Cohesion: 0.20
Nodes (4): django_db, TestAnalytics, TestForum, TestQuizzes

### Community 42 - "apply_subscription_updated"
Cohesion: 0.19
Nodes (11): apply_checkout_completed(), _apply_plan_code(), apply_subscription_deleted(), apply_subscription_updated(), plan_code_for_stripe_price(), Sync subscription after Stripe Checkout completes., Sync plan/status when Stripe subscription changes., Downgrade to the free plan when a paid subscription ends. (+3 more)

### Community 43 - "accounts/models.py"
Cohesion: 0.22
Nodes (8): AbstractBaseUser, EmailVerificationToken, Meta, User, UserProfile, ensure_profile(), receiver, PermissionsMixin

### Community 44 - "services.js"
Cohesion: 0.08
Nodes (26): CategoriesManagePage, EngagementPage, ForgotPasswordPage, MediaEditorPage, ResetPasswordPage, TopicDetailPage, EmailVerifyBanner(), ChevronLeft() (+18 more)

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
Cohesion: 0.13
Nodes (26): get_user_organization(), Return the user's primary organization (first membership), or None., _daily_cache_key(), enforce_budget(), get_daily_limit(), get_daily_usage(), increment_daily_usage(), Daily message quota for the AI tutor. Usage is counted in Redis for speed and… (+18 more)

### Community 50 - "test_tutor_retrieval.py"
Cohesion: 0.12
Nodes (21): set_current_organization(), extract_pdf_text(), get_attachment_text(), Extract and cache PDF text for an article attachment., Return plain text from PDF bytes; empty string on failure., _article_searchable_text(), _category_boost(), chunk_text() (+13 more)

### Community 51 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, baseUrl, checkJs, jsx, module, moduleResolution, target, types (+4 more)

### Community 52 - "Pre-launch checklist"
Cohesion: 0.10
Nodes (20): 10. Ongoing operations, 11. Organization invites, 12. Error monitoring (Sentry), 13. Database backups, 14. E2E testing, 1. Domain and TLS, 2. Backend secrets, 3. Database (+12 more)

### Community 53 - "create_organization_with_owner"
Cohesion: 0.16
Nodes (9): create_organization_with_owner(), generate_unique_slug(), Create an organization and make ``owner`` its owner member., django_db, TestAuditLogTenantScope, public_org(), fixture, django_db (+1 more)

### Community 54 - "sms_services.py"
Cohesion: 0.15
Nodes (23): PhoneOTP, SmsMessage, AfricasTalkingSmsProvider, BaseSmsProvider, DummySmsProvider, get_sms_provider(), normalize_phone(), Log SMS in development; always succeeds. (+15 more)

### Community 55 - "views/mfa.py"
Cohesion: 0.13
Nodes (20): consume_mfa_challenge(), generate_totp_secret(), provisioning_uri(), TOTP multi-factor authentication for privileged accounts., totp_for_secret(), user_has_mfa_enabled(), verify_totp_code(), Account-level permission helpers. (+12 more)

### Community 56 - "tenants/models.py"
Cohesion: 0.05
Nodes (53): api_view, Public platform branding strings., Badge, MediaAssetFilter, Meta, Media library API: CRUD + audio/video uploads., Article, ArticleProgress (+45 more)

### Community 57 - "test_tutor_providers.py"
Cohesion: 0.18
Nodes (11): _anthropic_configured(), get_tutor_provider(), _last_user_message(), _openai_configured(), Pluggable AI providers for the tutor. Mirrors ``apps/billing/providers.py``: a…, Resolve the active provider, degrading to the stub when credentials are missing., resolve_provider_name(), no_ai_credentials() (+3 more)

### Community 58 - "Production environment checklist — integrations"
Cohesion: 0.08
Nodes (25): 10. Compliance / monitoring gates (production), 2. Stripe billing (required for paid SaaS), 2b. No Stripe / unsupported country (e.g. Uganda), 3. SMS — Africa's Talking (optional), 4. Web push — VAPID (optional), 6. Enterprise SSO — OpenID Connect (optional), 7. Pre-flight validation, 8. Service env parity (Render / Docker) (+17 more)

### Community 59 - "CiSmokeUser"
Cohesion: 0.22
Nodes (4): CiSmokeUser, HttpUser, task, Lightweight Locust scenario for CI — avoids mass registration throttling.

### Community 60 - "_parse_stats"
Cohesion: 0.29
Nodes (8): main(), _parse_stats(), Path, Headless Locust smoke gate for CI. Runs a short read-heavy scenario and fails…, Return fail_ratio, p95_ms, failures, requests from Locust CSV stats., Path, Unit tests for Locust CI gate stats parsing (no live Locust run)., test_parse_stats_aggregated()

### Community 61 - "TestEmailVerification"
Cohesion: 0.14
Nodes (5): django_db, TestEmailVerification, TestLogoutBlacklist, TestSuspension, TestTokenRefresh

### Community 62 - "TutorUnavailable"
Cohesion: 0.21
Nodes (5): TutorUnavailable, AnthropicTutorProvider, OpenAICompatibleTutorProvider, Any OpenAI-compatible endpoint: OpenAI, Ollama, OpenRouter, Groq, Together., FailingProvider

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

### Community 67 - "tenants/permissions.py"
Cohesion: 0.12
Nodes (14): check_mfa_enrolled(), Raise ``MfaSetupRequired`` when a privileged user has not enrolled MFA., _can_see_unpublished(), CanDeleteOrgContent, get_membership(), IsOrgContentEditor, IsOrgForumModerator, IsOrgMember (+6 more)

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
Cohesion: 0.21
Nodes (9): issue_mfa_challenge(), EmailTokenObtainPairView, LoginView, LogoutView, APIView, Registration, login and logout., RegisterView, Account views. Split into cohesive submodules; every public view is re-exported… (+1 more)

### Community 76 - "Load testing (Locust)"
Cohesion: 0.17
Nodes (12): Background tasks (Celery + Redis), CI load-test gate, CI load-test gate, Eager fallback (dev / test), Getting meaningful numbers, Headless ramp toward the SRS concurrency target, Institutional scale notes (10k concurrent), Load testing (Locust) (+4 more)

### Community 77 - "Backend setup"
Cohesion: 0.15
Nodes (13): AI tutor (RAG), API reference, Backend setup, Background tasks (Celery), Civic Education RSS, Default accounts (after `seed_data`), Deployment (Render), Load testing (+5 more)

### Community 78 - "apply_article_translation"
Cohesion: 0.21
Nodes (6): apply_article_translation(), Fill the missing language side. Returns True when a write happened., source_fingerprint(), PrefixProvider, Returns the source text with a prefix so markdown structure is preserved., TestApplyArticleTranslation

### Community 79 - "session.py"
Cohesion: 0.20
Nodes (12): JWTCookieAuthentication, Cookie-aware JWT authentication. Checks httpOnly cookies first (preferred, more…, Authenticate via httpOnly cookie if present; fall back to Bearer header., check_session_idle(), is_privileged_user(), Server-side session controls: idle timeout and epoch-based revocation., Privileged sessions enforce idle timeout (platform staff or org admins)., Raise AuthenticationFailed if a privileged user has been idle too long. (+4 more)

### Community 80 - "Subscription"
Cohesion: 0.10
Nodes (17): PlanAdmin, register, SubscriptionAdmin, BillingConfig, AppConfig, Meta, Plan, A subscription tier with pricing and per-tenant quotas. (+9 more)

### Community 81 - "package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 83 - "Civic Education RSS — Frontend"
Cohesion: 0.22
Nodes (8): Civic Education RSS — Frontend, Deployment, Environment variables, Features, Local setup, Project structure, Requirements, Scripts

### Community 86 - "enable_mfa"
Cohesion: 0.23
Nodes (6): enable_mfa(), Enroll a test user in TOTP MFA (privileged routes require this)., django_db, TestMarkdownXss, TestMfaEnforcement, TestMfaLogin

### Community 87 - "DeactivateAccountView"
Cohesion: 0.20
Nodes (7): AvatarUploadView, DeactivateAccountView, MyDataExportView, APIView, extend_schema, Soft-deactivate the authenticated account., Download the authenticated user's personal data (GDPR-style).

### Community 88 - "TestTopicModeration"
Cohesion: 0.15
Nodes (5): django_db, TestCommentModeration, TestPendingQueue, TestTopicModeration, TestTopicVisibility

### Community 89 - "vercel.json"
Cohesion: 0.50
Nodes (3): buildCommand, outputDirectory, rewrites

### Community 96 - "Constitution & controlled documents"
Cohesion: 0.17
Nodes (12): 1. Add source files, 2. Run seed, 3. Verify, API path, Constitution & controlled documents, Option A — Seed data (recommended for demos), Option B — Article editor (production / org admins), Overview (+4 more)

### Community 97 - "StubTutorProvider"
Cohesion: 0.31
Nodes (3): Offline provider used when no AI credentials are configured., StubTutorProvider, TestStubProvider

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
Cohesion: 0.12
Nodes (20): UserRoleUpdateSerializer, _get_managed_user(), APIView, extend_schema, Moderator and admin actions on other users., Resolve a user visible in the current admin/moderator list., SuspendUserView, UnsuspendUserView (+12 more)

### Community 149 - "TestGlobalSearch"
Cohesion: 0.25
Nodes (3): django_db, TestGlobalSearch, TestTutorHistory

### Community 150 - "log_security_event"
Cohesion: 0.15
Nodes (13): custom_exception_handler(), MfaSetupRequired, APIException, Log permission denials and MFA setup blocks as security events., Meta, Persisted security events for platform-admin monitoring dashboards., SecurityEvent, _client_ip() (+5 more)

### Community 192 - "bump_session_epoch"
Cohesion: 0.25
Nodes (6): bump_session_epoch(), Invalidate all outstanding JWTs for this user by advancing session_epoch., extend_schema, APIView, SCIM User resource: get / patch / deactivate., ScimUserDetailView

### Community 196 - "_upload_media_file"
Cohesion: 0.27
Nodes (6): MediaAudioUploadView, MediaVideoUploadView, action, APIView, extend_schema, _upload_media_file()

### Community 198 - "Civic Education RSS API Reference"
Cohesion: 0.29
Nodes (7): Civic Education RSS API Reference, Conventions, Endpoint index, Gamification & engagement, Ops commands, Related docs, Tutor API (summary)

### Community 199 - "learning/signals.py"
Cohesion: 0.11
Nodes (21): enqueue_article_translation(), maintain_tutor_index(), notify_on_publish(), receiver, track_attachment_change(), build_tutor_index_text(), Build and maintain pre-indexed tutor search text on articles., Combine article body and PDF attachment text for tutor retrieval. (+13 more)

### Community 200 - "TestTutorChat"
Cohesion: 0.18
Nodes (3): django_db, TestTutorAdminUsage, TestTutorChat

### Community 201 - "Testing & CI"
Cohesion: 0.20
Nodes (10): Backend tests, CI pipeline (`.github/workflows/ci.yml`), E2E tests (Playwright), Environment variables (live e2e), Frontend unit tests (Vitest), Live backend (`e2e-live` CI job), Mocked API (default — `frontend` CI job), Ops smoke (loadtest job) (+2 more)

### Community 202 - "TestSmsAlerts"
Cohesion: 0.25
Nodes (3): django_db, TestPhoneOtp, TestSmsAlerts

### Community 203 - "TestContentPacks"
Cohesion: 0.20
Nodes (4): django_db, TestContentPacks, TestOrgRoleRBAC, TestPlatformSupportAndSecurity

### Community 206 - "GlobalSearchView"
Cohesion: 0.40
Nodes (3): GlobalSearchView, APIView, extend_schema

### Community 210 - "prompts.py"
Cohesion: 0.36
Nodes (5): normalize_language(), Shared application constants., Return ``en`` or ``ar``; any other value maps to ``en``., System prompt construction for the AI tutor., _user_language()

### Community 211 - "accounts/serializers.py"
Cohesion: 0.14
Nodes (15): AnonRateThrottle, PasswordResetConfirmSerializer, PasswordResetOtpConfirmSerializer, PasswordResetOtpRequestSerializer, PasswordResetRequestSerializer, ChangePasswordView, PasswordResetConfirmView, PasswordResetOtpConfirmView (+7 more)

### Community 212 - "test_org_analytics.py"
Cohesion: 0.60
Nodes (4): free_plan(), org_admin_member(), pro_plan(), fixture

### Community 216 - "Notification"
Cohesion: 0.14
Nodes (12): register, SmsMessageAdmin, WebPushSubscriptionAdmin, Notification, notify_user(), Create a single notification for one user (cheap, stays inline)., broadcast_notification_task(), Fan out an in-app notification to active users in batches. (+4 more)

### Community 217 - "BaseTutorProvider"
Cohesion: 0.15
Nodes (8): BaseTutorProvider, Runs a tutor turn against whichever AI provider is configured., TutorService, FailingProvider, django_db, Honors the (text, 0) deltas then ('', total_tokens) terminal contract., RecordingProvider, TestServiceHonorsProviderContract

### Community 218 - "1. Celery + Redis (required)"
Cohesion: 0.40
Nodes (5): 1. Celery + Redis (required), Backend environment, Deploy checklist, Render, Verify

### Community 221 - "log_activity"
Cohesion: 0.14
Nodes (8): _client_meta(), compute_integrity_hash(), log_activity(), Verify hash-chain integrity for recent activity logs., verify_audit_chain(), MediaAssetViewSet, django_db, TestBackfillAuditOrgs

### Community 223 - "test_product_features.py"
Cohesion: 0.16
Nodes (6): django_db, TestAuditLogs, TestPhoneVerification, TestResendVerificationEmail, TestUnsuspendUser, TestWebPushSubscribe

### Community 226 - "5. AI tutor (optional)"
Cohesion: 0.40
Nodes (5): 5. AI tutor (optional), Backend environment, Checklist, Free option for testing, Verify

### Community 241 - "core/serializers.py"
Cohesion: 0.40
Nodes (4): DetailSerializer, MessageSerializer, Generic ``{"detail": "..."}`` response body., Generic ``{"message": "..."}`` response body.

## Knowledge Gaps
- **268 isolated node(s):** `Migration`, `Migration`, `Migration`, `Migration`, `Migration` (+263 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **79 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_current_organization()` connect `get_current_organization` to `quizzes/views.py`, `analytics/views.py`, `ArticleViewSet`, `core/middleware.py`, `billing/views.py`, `notifications/views.py`, `user_management.py`, `Membership`, `ArticleSerializer`, `ActivityLog`, `engagement/views.py`, `sms_views.py`, `tutor/services.py`, `sms_services.py`, `tenants/models.py`, `grade_a_views.py`, `tenants/permissions.py`, `_upload_media_file`, `prompts.py`, `log_activity`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `Article` connect `tenants/models.py` to `quizzes/views.py`, `analytics/views.py`, `translation.py`, `learning/signals.py`, `test_article_translation.py`, `ArticleViewSet`, `apply_article_translation`, `tutor/services.py`, `prompts.py`, `test_tutor_retrieval.py`, `ArticleSerializer`, `test_saas.py`, `get_current_organization`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `Membership` connect `Membership` to `scim.py`, `quizzes/views.py`, `Organization`, `forum/views.py`, `test_grade_a_enterprise.py`, `user_management.py`, `conftest.py`, `log_security_event`, `test_saas.py`, `get_current_organization`, `tutor/services.py`, `create_organization_with_owner`, `sms_services.py`, `views/mfa.py`, `tenants/models.py`, `tenants/permissions.py`, `session.py`, `backfill_audit_orgs.py`, `Subscription`, `test_org_analytics.py`, `log_activity`, `TenantMiddleware`, `test_product_features.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `Membership` (e.g. with `TenantMiddleware` and `CanDeleteOrgContent`) actually correct?**
  _`Membership` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Migration`, `Migration`, `Migration` to the rest of the system?**
  _268 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `UserSerializer` be split into smaller, more focused modules?**
  _Cohesion score 0.14166666666666666 - nodes in this community are weakly interconnected._
- **Should `quizzes/views.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05661005661005661 - nodes in this community are weakly interconnected._