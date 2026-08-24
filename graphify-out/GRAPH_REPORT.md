# Graph Report - Civic Education Platform  (2026-08-24)

## Corpus Check
- 446 files · ~172,824 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2826 nodes · 6475 edges · 239 communities (159 shown, 80 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 339 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `77d746e4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- quizzes/models.py
- scim.py
- quizzes/views.py
- analytics/views.py
- sso.py
- ui.jsx
- forum/views.py
- urls/auth.py
- get_current_organization
- ArticleViewSet
- bind_client_to_org
- BillingPage.jsx
- App.jsx
- useAuth
- core/middleware.py
- Icons.jsx
- billing/views.py
- ArticleDetailPage.jsx
- log_activity
- notifications/views.py
- tenants/views.py
- ArticleEditorPage.jsx
- TutorPage.jsx
- Category
- billing/services.py
- ActivityLog
- tutor/views.py
- TestBilling
- dependencies
- TutorChat
- OrganizationSsoConfigSerializer
- integrations.py
- seed_data.py
- devDependencies
- get_preferred_language
- sms_views.py
- django_db
- translation.py
- eslint
- Notification
- test_article_translation.py
- TestForum
- ArticleSerializer
- Role
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
- views/__init__.py
- Article
- test_tutor_providers.py
- Production environment checklist — integrations
- CiSmokeUser
- _parse_stats
- core/permissions.py
- TutorUnavailable
- Command
- test_api.py
- APIView
- scripts
- learning/views.py
- TestOrganizationInvites
- TestNotifications
- helpers.js
- sms_providers.py
- main.jsx
- Command
- TenantsConfig
- TestArticleI18n
- Load testing (Locust)
- Backend setup
- tenants/admin.py
- session.py
- Membership
- package.json
- AccountsConfig
- Civic Education RSS — Frontend
- LearningConfig
- 0003_migrate_primary_color_to_green.py
- conftest.py
- upload_file
- TestTopicModeration
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
- QuizEditorPage.jsx
- @testing-library/user-event
- Compliance readiness (SOC 2 / ISO 27001)
- Disaster recovery
- @vitejs/plugin-react
- accounts/serializers.py
- TestGlobalSearch
- Command
- BillingConfig
- normalize_primary_color
- TestLearningProgress
- Civic Education RSS API Reference
- learning/signals.py
- TestTutorChat
- Testing & CI
- TestSmsAlerts
- test_enterprise_gaps.py
- ArticleFilter
- jwt.js
- TestInAppBroadcast
- Command
- 0009_learning_progress.py
- 0006_phone_verified_activity_type.py
- prompts.py
- password.py
- tailwindcss
- @testing-library/jest-dom
- @testing-library/react
- broadcast_notification_task
- RecordingProvider
- 1. Celery + Redis (required)
- EngagementConfig
- GamificationConfig
- TenantMiddleware
- django_db
- 5. AI tutor (optional)
- globals
- @playwright/test
- start.sh
- 0006_userprofile_xp_points.py
- engagement/migrations/0001_initial.py
- gamification/migrations/0001_initial.py
- 0010_article_tutor_index_text_mediaasset_captions_url.py
- 0011_article_translation.py
- @vitest/coverage-v8

## God Nodes (most connected - your core abstractions)
1. `bind_client_to_org()` - 113 edges
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

## Communities (239 total, 80 thin omitted)

### Community 0 - "quizzes/models.py"
Cohesion: 0.22
Nodes (9): Certificate, Meta, Question, Quiz, QuizAttempt, QuestionSerializer, QuestionWriteSerializer, bilingual_article() (+1 more)

### Community 1 - "scim.py"
Cohesion: 0.12
Nodes (19): bump_session_epoch(), Invalidate all outstanding JWTs for this user by advancing session_epoch., extend_schema, authenticate_scim(), _group_to_scim(), APIView, SCIM 2.0 Groups — mapped to organization departments., ScimGroupDetailView (+11 more)

### Community 2 - "quizzes/views.py"
Cohesion: 0.14
Nodes (14): CertificateSerializer, Meta, QuizAttemptSerializer, QuizAttemptSubmitSerializer, QuizSerializer, QuizWriteSerializer, generate_certificate_number(), CertificateDownloadView (+6 more)

### Community 3 - "analytics/views.py"
Cohesion: 0.10
Nodes (33): IsOrgAnalyticsAdmin, BasePermission, Organization owner or admin (analytics plan checked in the view)., _attempts_queryset(), build_dashboard_summary(), build_institutional_report_pdf(), build_member_progress(), build_my_learning_summary() (+25 more)

### Community 4 - "sso.py"
Cohesion: 0.07
Nodes (47): build_authorize_url(), claims_from_tokens(), exchange_code_for_tokens(), _fetch_jwks(), fetch_oidc_metadata(), fetch_userinfo(), get_or_create_user_from_sso(), get_org_sso_config() (+39 more)

### Community 5 - "ui.jsx"
Cohesion: 0.10
Nodes (38): CertificatesPage, QuizzesPage, GamificationSummary(), Trophy(), Pagination(), Alert(), CardSkeleton(), ConfirmDialog() (+30 more)

### Community 6 - "forum/views.py"
Cohesion: 0.07
Nodes (30): Prefer official PDF in seed_assets/ if present, else sample., resolve_constitution_attachment(), DiscussionComment, DiscussionTopic, Meta, CommentCreateSerializer, DiscussionCommentSerializer, DiscussionTopicCreateSerializer (+22 more)

### Community 7 - "urls/auth.py"
Cohesion: 0.09
Nodes (19): PhoneVerifyConfirmSerializer, APIView, SsoCallbackView, SsoLoginView, SsoStatusView, CookieAwareTokenRefreshSerializer, CookieTokenRefreshView, Cookie-aware JWT refresh — accepts refresh from body or httpOnly cookie. (+11 more)

### Community 8 - "get_current_organization"
Cohesion: 0.12
Nodes (5): get_current_organization(), DepartmentListCreateView, Manager that automatically scopes queries to the current organization. When a…, TenantManager, TenantQuerySet

### Community 9 - "ArticleViewSet"
Cohesion: 0.15
Nodes (8): ArticleAttachmentUploadView, ArticleImageUploadView, ArticleViewSet, action, APIView, extend_schema, Upload a PDF or document attachment for an article (e.g. full constitution…, Upload an image for featured media or inline markdown embeds.

### Community 10 - "bind_client_to_org"
Cohesion: 0.08
Nodes (11): bind_client_to_org(), Authenticate and scope requests to ``org`` (creates membership if needed)., TestArticles, django_db, TestMediaLibraryApi, django_db, TestOrgAnalytics, TestCertificateTask (+3 more)

### Community 11 - "BillingPage.jsx"
Cohesion: 0.09
Nodes (21): BillingPage, AuthShell(), FEATURES, PlatformLogo(), UsageBar(), PLATFORM_LOGO_ALT, PLATFORM_LOGO_URL, PLATFORM_NAME (+13 more)

### Community 12 - "App.jsx"
Cohesion: 0.09
Nodes (17): ArticleDetailPage, ArticlesManagePage, ArticlesPage, ContactPage, DashboardPage, ForumPage, MediaDetailPage, MediaManagePage (+9 more)

### Community 13 - "useAuth"
Cohesion: 0.05
Nodes (47): AcceptInvitePage, AdminPage, OrganizationPage, SsoCallbackPage, ArrowUp(), Moon(), Sun(), InstallPrompt() (+39 more)

### Community 14 - "core/middleware.py"
Cohesion: 0.08
Nodes (15): client_ip_from_request(), ip_allowed(), IP allowlist helpers and read-replica database router., Return True when allowlist is empty or client_ip matches an entry., Route reads to DATABASES['replica'] when configured., ReadReplicaRouter, ContentSecurityPolicyMiddleware, IpAllowlistMiddleware (+7 more)

### Community 15 - "Icons.jsx"
Cohesion: 0.16
Nodes (18): NotificationsPage, Breadcrumb(), AcademicCap(), Bell(), BookOpen(), ChatBubble(), ChevronRight(), CloudArrowDown() (+10 more)

### Community 16 - "billing/views.py"
Cohesion: 0.08
Nodes (22): BaseBillingProvider, CheckoutResult, DummyBillingProvider, get_billing_provider(), Pluggable billing providers. The ``dummy`` provider requires no external…, No-op provider for local dev/tests; activates plans instantly., StripeBillingProvider, CheckoutSerializer (+14 more)

### Community 17 - "ArticleDetailPage.jsx"
Cohesion: 0.10
Nodes (34): QuizTakePage, OfflineBanner(), useDebouncedValue(), useOnlineStatus(), api, readingTime(), plainTextExcerpt(), SANITIZE_OPTIONS (+26 more)

### Community 18 - "log_activity"
Cohesion: 0.09
Nodes (21): AvatarUploadView, DeactivateAccountView, MyDataExportView, APIView, Self-service profile, avatar, data export and deactivation., Soft-deactivate the authenticated account., Download the authenticated user's personal data (GDPR-style)., _client_meta() (+13 more)

### Community 19 - "notifications/views.py"
Cohesion: 0.13
Nodes (19): BroadcastNotificationSerializer, WebPushSubscribeSerializer, WebPushSubscription, cleanup_push_subscriptions(), push_subscription_stats(), notify_all_users(), Fan out a notification to all active users via a background task. When…, BroadcastNotificationView (+11 more)

### Community 20 - "tenants/views.py"
Cohesion: 0.08
Nodes (37): DepartmentDetailView, OrganizationInvite, Pending email invitation to join an organization., InvitePreviewSerializer, MemberInviteSerializer, MemberRoleUpdateSerializer, MembershipSerializer, Meta (+29 more)

### Community 21 - "ArticleEditorPage.jsx"
Cohesion: 0.18
Nodes (11): ArticleEditorPage, MediaPlayer(), renderMarkdown(), API_ORIGIN, resolveMediaUrl(), getEmbedInfo(), ArticleEditorPage(), EMPTY_FORM (+3 more)

### Community 22 - "TutorPage.jsx"
Cohesion: 0.14
Nodes (22): TutorPage, LanguageSwitcher(), applyDirection(), initial, DEFAULT_LANGUAGE, normalizeLanguage(), RTL_LANGUAGES, sanitizeStoredLanguage() (+14 more)

### Community 23 - "Category"
Cohesion: 0.10
Nodes (12): api_view, Category, CategorySerializer, MediaAssetSerializer, Meta, validate_http_url(), content_bundle(), ContentBundleThrottle (+4 more)

### Community 24 - "billing/services.py"
Cohesion: 0.09
Nodes (32): extend_schema, AnalyticsNotAvailable, apply_checkout_completed(), _apply_plan_code(), apply_subscription_deleted(), apply_subscription_updated(), check_quota(), count_usage() (+24 more)

### Community 25 - "ActivityLog"
Cohesion: 0.19
Nodes (8): ActivityLog, Meta, ActivityLogSerializer, Meta, ActivityLogExportView, ActivityLogListView, APIView, Export org activity logs as CSV or JSON for compliance reviews.

### Community 26 - "tutor/views.py"
Cohesion: 0.13
Nodes (22): ChatRequestSerializer, ChatResponseSerializer, TutorMessageSerializer, TutorSessionSerializer, TutorSessionSummarySerializer, TutorSourceSerializer, TutorUsageSerializer, get_tutor_service() (+14 more)

### Community 27 - "TestBilling"
Cohesion: 0.15
Nodes (5): django_db, TestBilling, TestMyOrganizations, TestOrganizationRegistration, TestQuotas

### Community 28 - "dependencies"
Cohesion: 0.08
Nodes (25): axios, dompurify, dependencies, axios, dompurify, i18next, i18next-browser-languagedetector, idb (+17 more)

### Community 29 - "TutorChat"
Cohesion: 0.14
Nodes (10): register, TutorChatAdmin, get_chat_session_history(), list_chat_sessions(), Read access to persisted tutor conversations., Return ordered messages for a persisted session owned by the user., Summarize recent tutor conversations persisted for the user., TutorChat (+2 more)

### Community 30 - "OrganizationSsoConfigSerializer"
Cohesion: 0.10
Nodes (13): BulkMemberImportView, _org_support_snapshot(), OrganizationSsoConfigView, PlatformOrganizationDetailView, PlatformOrganizationListView, PlatformUsageSummaryView, APIView, extend_schema (+5 more)

### Community 31 - "integrations.py"
Cohesion: 0.08
Nodes (36): build_integrations_report(), check_cache(), check_celery(), check_database(), check_email(), check_oidc(), check_pypdf(), check_sentry() (+28 more)

### Community 32 - "seed_data.py"
Cohesion: 0.06
Nodes (49): absolute_media_url(), Command, load_constitution_text(), BaseCommand, Campaign, Meta, Petition, PetitionSignature (+41 more)

### Community 33 - "devDependencies"
Cohesion: 0.09
Nodes (23): autoprefixer, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, devDependencies, autoprefixer, @eslint/js, eslint-plugin-react-hooks (+15 more)

### Community 34 - "get_preferred_language"
Cohesion: 0.20
Nodes (4): get_preferred_language(), Resolve API content language to ``en`` or ``ar`` only., MediaAssetSummarySerializer, Compact nested representation for articles.

### Community 35 - "sms_views.py"
Cohesion: 0.19
Nodes (14): require_sms(), BroadcastSmsSerializer, Meta, SendSmsSerializer, SmsMessageSerializer, BroadcastSmsView, PlatformBroadcastSmsView, APIView (+6 more)

### Community 36 - "django_db"
Cohesion: 0.17
Nodes (5): django_db, TestEngagement, TestGamification, TestMediaCaptions, TestTutorStream

### Community 37 - "translation.py"
Cohesion: 0.10
Nodes (22): Command, BaseCommand, Enqueue automatic translation for articles missing English or Arabic., shared_task, Fill the missing English or Arabic side of an article., translate_article_task(), apply_article_translation(), _build_updates() (+14 more)

### Community 39 - "Notification"
Cohesion: 0.09
Nodes (24): register, SmsMessageAdmin, WebPushSubscriptionAdmin, Push a notification dict to all WebSocket connections for ``user_pk``. Call…, send_notification_to_user(), _get_or_create_prefs(), notify_user(), Unified notification fan-out. Call :func:`notify_user` to deliver a… (+16 more)

### Community 40 - "test_article_translation.py"
Cohesion: 0.13
Nodes (13): chunk_markdown(), detect_language(), Return ``ar`` when Arabic letters outnumber Latin letters, else ``en``., Split on blank-line paragraph boundaries, keeping chunks under max_chars., english_article(), django_db, fixture, TestChunkMarkdown (+5 more)

### Community 41 - "TestForum"
Cohesion: 0.20
Nodes (4): django_db, TestAnalytics, TestForum, TestQuizzes

### Community 43 - "Role"
Cohesion: 0.06
Nodes (21): AbstractBaseUser, Command, BaseCommand, EmailVerificationToken, Meta, Role, User, UserManager (+13 more)

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

### Community 49 - "tutor/services.py"
Cohesion: 0.12
Nodes (27): _daily_cache_key(), enforce_budget(), get_daily_limit(), get_daily_usage(), increment_daily_usage(), Daily message quota for the AI tutor. Usage is counted in Redis for speed and…, Return today's usage from Redis cache, seeding from DB on cold miss., Increment Redis counter and persist to DB asynchronously. (+19 more)

### Community 50 - "test_tutor_retrieval.py"
Cohesion: 0.09
Nodes (31): build_tutor_index_text(), Build and maintain pre-indexed tutor search text on articles., Combine article body and PDF attachment text for tutor retrieval., _cache_key(), extract_pdf_text(), fetch_attachment_bytes(), get_attachment_text(), _local_media_path() (+23 more)

### Community 51 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, baseUrl, checkJs, jsx, module, moduleResolution, target, types (+4 more)

### Community 52 - "Pre-launch checklist"
Cohesion: 0.10
Nodes (20): 10. Ongoing operations, 11. Organization invites, 12. Error monitoring (Sentry), 13. Database backups, 14. E2E testing, 1. Domain and TLS, 2. Backend secrets, 3. Database (+12 more)

### Community 53 - "create_organization_with_owner"
Cohesion: 0.11
Nodes (13): create_organization_with_owner(), generate_unique_slug(), Create an organization and make ``owner`` its owner member., django_db, TestAuditLogTenantScope, public_org(), fixture, django_db (+5 more)

### Community 54 - "sms_services.py"
Cohesion: 0.21
Nodes (18): PhoneOTP, SmsMessage, normalize_phone(), Normalize to E.164 for South Sudan (+211)., create_sms_log(), deliver_sms(), issue_phone_otp(), org_member_phones() (+10 more)

### Community 55 - "views/__init__.py"
Cohesion: 0.07
Nodes (41): AnonRateThrottle, consume_mfa_challenge(), generate_totp_secret(), issue_mfa_challenge(), provisioning_uri(), TOTP multi-factor authentication for privileged accounts., totp_for_secret(), user_has_mfa_enabled() (+33 more)

### Community 56 - "Article"
Cohesion: 0.08
Nodes (29): _can_see_unpublished(), MediaAssetFilter, MediaAssetViewSet, MediaAudioUploadView, MediaVideoUploadView, Meta, action, APIView (+21 more)

### Community 57 - "test_tutor_providers.py"
Cohesion: 0.12
Nodes (14): _anthropic_configured(), get_tutor_provider(), _last_user_message(), _openai_configured(), Pluggable AI providers for the tutor. Mirrors ``apps/billing/providers.py``: a…, Resolve the active provider, degrading to the stub when credentials are missing., Offline provider used when no AI credentials are configured., resolve_provider_name() (+6 more)

### Community 58 - "Production environment checklist — integrations"
Cohesion: 0.08
Nodes (25): 10. Compliance / monitoring gates (production), 2. Stripe billing (required for paid SaaS), 2b. No Stripe / unsupported country (e.g. Uganda), 3. SMS — Africa's Talking (optional), 4. Web push — VAPID (optional), 6. Enterprise SSO — OpenID Connect (optional), 7. Pre-flight validation, 8. Service env parity (Render / Docker) (+17 more)

### Community 59 - "CiSmokeUser"
Cohesion: 0.23
Nodes (4): CiSmokeUser, HttpUser, task, Lightweight Locust scenario for CI — avoids mass registration throttling.

### Community 60 - "_parse_stats"
Cohesion: 0.29
Nodes (8): main(), _parse_stats(), Path, Headless Locust smoke gate for CI. Runs a short read-heavy scenario and fails…, Return fail_ratio, p95_ms, failures, requests from Locust CSV stats., Path, Unit tests for Locust CI gate stats parsing (no live Locust run)., test_parse_stats_aggregated()

### Community 61 - "core/permissions.py"
Cohesion: 0.27
Nodes (10): IsAdmin, IsCitizenOrAbove, IsEditor, IsEditorOrAdmin, IsModerator, IsModeratorOrAdmin, IsOwnerOrAdmin, BasePermission (+2 more)

### Community 62 - "TutorUnavailable"
Cohesion: 0.13
Nodes (8): APIException, TutorUnavailable, AnthropicTutorProvider, BaseTutorProvider, OpenAICompatibleTutorProvider, Any OpenAI-compatible endpoint: OpenAI, Ollama, OpenRouter, Groq, Together., FailingProvider, FailingProvider

### Community 63 - "Command"
Cohesion: 0.31
Nodes (4): Command, BaseCommand, Path, Create a PostgreSQL logical backup using pg_dump.

### Community 64 - "test_api.py"
Cohesion: 0.20
Nodes (5): category(), django_db, fixture, TestAuth, TestHealthCheck

### Community 65 - "APIView"
Cohesion: 0.09
Nodes (15): AuditIntegrityVerifyView, ComplianceEvidencePackView, _hash_token(), PlatformSupportCaseListView, PlatformSupportCaseUpdateView, APIView, Download a compliance evidence pack for audits (ISO/SOC-style evidence)., Service-level objective snapshot for ops / enterprise reporting. (+7 more)

### Community 66 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, lint, preview, test, test:e2e, test:e2e:live (+1 more)

### Community 67 - "learning/views.py"
Cohesion: 0.09
Nodes (19): check_mfa_enrolled(), Account-level permission helpers., Raise ``MfaSetupRequired`` when a privileged user has not enrolled MFA., MfaSetupRequired, APIException, _can_publish_directly(), _can_see_unpublished(), CategoryViewSet (+11 more)

### Community 70 - "helpers.js"
Cohesion: 0.19
Nodes (11): API, apiGlob(), LIVE_ADMIN_EMAIL, LIVE_ADMIN_PASSWORD, LIVE_API, LIVE_ORG_SLUG, liveAuthHeaders(), loginLive() (+3 more)

### Community 71 - "sms_providers.py"
Cohesion: 0.29
Nodes (6): AfricasTalkingSmsProvider, BaseSmsProvider, DummySmsProvider, get_sms_provider(), Log SMS in development; always succeeds., SmsSendResult

### Community 72 - "main.jsx"
Cohesion: 0.19
Nodes (6): App(), guard(), ErrorBoundary, queryClient, captureUiError(), initSentry()

### Community 73 - "Command"
Cohesion: 0.33
Nodes (3): Command, BaseCommand, Management command: report English/Arabic bilingual content completeness.…

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

### Community 78 - "tenants/admin.py"
Cohesion: 0.60
Nodes (4): MembershipAdmin, OrganizationAdmin, OrganizationInviteAdmin, register

### Community 79 - "session.py"
Cohesion: 0.20
Nodes (12): JWTCookieAuthentication, Cookie-aware JWT authentication. Checks httpOnly cookies first (preferred, more…, Authenticate via httpOnly cookie if present; fall back to Bearer header., check_session_idle(), is_privileged_user(), Server-side session controls: idle timeout and epoch-based revocation., Privileged sessions enforce idle timeout (platform staff or org admins)., Raise AuthenticationFailed if a privileged user has been idle too long. (+4 more)

### Community 80 - "Membership"
Cohesion: 0.06
Nodes (42): PlanAdmin, register, SubscriptionAdmin, Meta, Plan, A subscription tier with pricing and per-tenant quotas., Subscription, clear_current_organization() (+34 more)

### Community 81 - "package.json"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 83 - "Civic Education RSS — Frontend"
Cohesion: 0.22
Nodes (8): Civic Education RSS — Frontend, Deployment, Environment variables, Features, Local setup, Project structure, Requirements, Scripts

### Community 86 - "conftest.py"
Cohesion: 0.12
Nodes (19): admin_user(), api_client(), category(), citizen_user(), editor_user(), enable_mfa(), login_user(), moderator_user() (+11 more)

### Community 87 - "upload_file"
Cohesion: 0.20
Nodes (12): extend_schema, get_signed_url(), get_supabase_client(), _local_media_url(), _save_local_file(), upload_bytesio(), upload_file(), generate_certificate_pdf() (+4 more)

### Community 88 - "TestTopicModeration"
Cohesion: 0.15
Nodes (5): django_db, TestCommentModeration, TestPendingQueue, TestTopicModeration, TestTopicVisibility

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

### Community 143 - "QuizEditorPage.jsx"
Cohesion: 0.50
Nodes (7): QuizEditorPage, buildPayload(), emptyQuestion(), optionsArMismatch(), optionsFromText(), questionFromApi(), QuizEditorPage()

### Community 145 - "Compliance readiness (SOC 2 / ISO 27001)"
Cohesion: 0.33
Nodes (6): Compliance readiness (SOC 2 / ISO 27001), Control matrix, Evidence pack (in-product), Production security baseline (must be true before audit), Recurring ops (auditor will ask), What certification still requires (outside this repo)

### Community 146 - "Disaster recovery"
Cohesion: 0.33
Nodes (6): Automated backup, CI, Disaster recovery, Manual restore (true incident), Restore drill (required before audits), RPO / RTO targets (ops commitment)

### Community 148 - "accounts/serializers.py"
Cohesion: 0.11
Nodes (19): Platform admins and organization owners/admins must use MFA when org requires…, user_requires_mfa(), Meta, ProfileUpdateSerializer, RegisterSerializer, RoleSerializer, UserProfileSerializer, UserRoleUpdateSerializer (+11 more)

### Community 149 - "TestGlobalSearch"
Cohesion: 0.25
Nodes (3): django_db, TestGlobalSearch, TestTutorHistory

### Community 198 - "Civic Education RSS API Reference"
Cohesion: 0.29
Nodes (7): Civic Education RSS API Reference, Conventions, Endpoint index, Gamification & engagement, Ops commands, Related docs, Tutor API (summary)

### Community 199 - "learning/signals.py"
Cohesion: 0.25
Nodes (8): enqueue_article_translation(), maintain_tutor_index(), notify_on_publish(), receiver, track_attachment_change(), invalidate_attachment_text_cache(), Drop cached PDF text when an article attachment changes., TestTutorIndex

### Community 200 - "TestTutorChat"
Cohesion: 0.20
Nodes (3): django_db, TestTutorAdminUsage, TestTutorChat

### Community 201 - "Testing & CI"
Cohesion: 0.20
Nodes (10): Backend tests, CI pipeline (`.github/workflows/ci.yml`), E2E tests (Playwright), Environment variables (live e2e), Frontend unit tests (Vitest), Live backend (`e2e-live` CI job), Mocked API (default — `frontend` CI job), Ops smoke (loadtest job) (+2 more)

### Community 202 - "TestSmsAlerts"
Cohesion: 0.25
Nodes (3): django_db, TestPhoneOtp, TestSmsAlerts

### Community 203 - "test_enterprise_gaps.py"
Cohesion: 0.14
Nodes (8): Meta, Persisted security events for platform-admin monitoring dashboards., SecurityEvent, django_db, Tests for remaining enterprise gaps: org RBAC, content packs, platform support., TestContentPacks, TestOrgRoleRBAC, TestPlatformSupportAndSecurity

### Community 210 - "prompts.py"
Cohesion: 0.26
Nodes (9): normalize_language(), Shared application constants., Return ``en`` or ``ar``; any other value maps to ``en``., get_user_organization(), Return the user's primary organization (first membership), or None., build_system_prompt(), System prompt construction for the AI tutor., _user_language() (+1 more)

### Community 211 - "password.py"
Cohesion: 0.12
Nodes (16): PasswordResetConfirmSerializer, PasswordResetOtpConfirmSerializer, PasswordResetOtpRequestSerializer, PasswordResetRequestSerializer, ChangePasswordView, PasswordResetConfirmView, PasswordResetOtpConfirmView, PasswordResetOtpRequestView (+8 more)

### Community 216 - "broadcast_notification_task"
Cohesion: 0.50
Nodes (3): broadcast_notification_task(), Fan out an in-app notification to active users in batches., TestBroadcastTask

### Community 217 - "RecordingProvider"
Cohesion: 0.29
Nodes (4): django_db, Honors the (text, 0) deltas then ('', total_tokens) terminal contract., RecordingProvider, TestServiceHonorsProviderContract

### Community 218 - "1. Celery + Redis (required)"
Cohesion: 0.40
Nodes (5): 1. Celery + Redis (required), Backend environment, Deploy checklist, Render, Verify

### Community 223 - "django_db"
Cohesion: 0.12
Nodes (7): django_db, TestAuditLogs, TestAvatarUpload, TestPhoneVerification, TestResendVerificationEmail, TestUnsuspendUser, TestWebPushSubscribe

### Community 226 - "5. AI tutor (optional)"
Cohesion: 0.40
Nodes (5): 5. AI tutor (optional), Backend environment, Checklist, Free option for testing, Verify

## Knowledge Gaps
- **269 isolated node(s):** `Migration`, `Migration`, `Migration`, `Migration`, `Migration` (+264 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **80 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_current_organization()` connect `get_current_organization` to `quizzes/views.py`, `analytics/views.py`, `forum/views.py`, `ArticleViewSet`, `core/middleware.py`, `billing/views.py`, `log_activity`, `notifications/views.py`, `accounts/serializers.py`, `tenants/views.py`, `Category`, `ActivityLog`, `OrganizationSsoConfigSerializer`, `seed_data.py`, `sms_views.py`, `ArticleSerializer`, `tutor/services.py`, `sms_services.py`, `Article`, `APIView`, `learning/views.py`, `Membership`, `prompts.py`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Why does `Article` connect `Article` to `seed_data.py`, `test_api.py`, `quizzes/models.py`, `learning/views.py`, `analytics/views.py`, `translation.py`, `forum/views.py`, `learning/signals.py`, `test_article_translation.py`, `ArticleViewSet`, `ArticleSerializer`, `ArticleFilter`, `Membership`, `tutor/services.py`, `prompts.py`, `test_tutor_retrieval.py`, `Category`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `bind_client_to_org()` connect `bind_client_to_org` to `quizzes/models.py`, `forum/views.py`, `log_activity`, `accounts/serializers.py`, `tenants/views.py`, `TestGlobalSearch`, `Category`, `ActivityLog`, `integrations.py`, `seed_data.py`, `django_db`, `Notification`, `TestForum`, `test_deploy.py`, `tutor/services.py`, `create_organization_with_owner`, `Article`, `test_api.py`, `TestOrganizationInvites`, `TestLearningProgress`, `TestTutorChat`, `TestSmsAlerts`, `test_enterprise_gaps.py`, `TestArticleI18n`, `TestInAppBroadcast`, `Membership`, `conftest.py`, `TestTopicModeration`, `django_db`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `Membership` (e.g. with `TenantMiddleware` and `CanDeleteOrgContent`) actually correct?**
  _`Membership` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Migration`, `Migration`, `Migration` to the rest of the system?**
  _269 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `scim.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1226890756302521 - nodes in this community are weakly interconnected._
- **Should `quizzes/views.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14461538461538462 - nodes in this community are weakly interconnected._