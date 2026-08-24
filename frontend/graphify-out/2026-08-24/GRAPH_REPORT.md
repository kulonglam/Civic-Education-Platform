# Graph Report - frontend  (2026-08-24)

## Corpus Check
- 142 files · ~83,609 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 565 nodes · 1636 edges · 36 communities (35 shown, 1 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 17 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0f7f6397`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- App.jsx
- ArticleDetailPage.jsx
- Icons.jsx
- devDependencies
- dependencies
- api.js
- ui.jsx
- ArticleEditorPage.jsx
- helpers.js
- Layout.jsx
- services.js
- useAuth
- extractError
- main.jsx
- compilerOptions
- OrganizationPage.jsx
- Civic Education RSS — Frontend
- BillingPage.jsx
- QuizEditorPage.jsx
- BookmarkButton.jsx
- LanguageSwitcher.jsx
- vercel.json
- AdminPage.test.jsx

## God Nodes (most connected - your core abstractions)
1. `extractError()` - 63 edges
2. `useAuth()` - 51 edges
3. `formatDate()` - 37 edges
4. `Alert()` - 35 edges
5. `Spinner()` - 30 edges
6. `useOrganization()` - 30 edges
7. `queryKeys` - 29 edges
8. `PageHeader()` - 28 edges
9. `EmptyState()` - 18 edges
10. `normalizeLanguage()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `EngagementPage()` --calls--> `extractError()`  [EXTRACTED]
  src/pages/EngagementPage.jsx → src/lib/api.js
- `MediaEditorPage()` --calls--> `extractError()`  [EXTRACTED]
  src/pages/MediaEditorPage.jsx → src/lib/api.js
- `ResetPasswordPage()` --calls--> `extractError()`  [EXTRACTED]
  src/pages/ResetPasswordPage.jsx → src/lib/api.js
- `NotificationsPage()` --calls--> `formatDate()`  [EXTRACTED]
  src/pages/NotificationsPage.jsx → src/lib/format.js
- `App()` --calls--> `startOfflineSync()`  [EXTRACTED]
  src/App.jsx → src/lib/offline/sync.js

## Import Cycles
- None detected.

## Communities (36 total, 1 thin omitted)

### Community 0 - "App.jsx"
Cohesion: 0.05
Nodes (65): ArticleDetailPage, ArticlesManagePage, ArticlesPage, CategoriesManagePage, CertificatesPage, ContactPage, EngagementPage, ForumPage (+57 more)

### Community 1 - "ArticleDetailPage.jsx"
Cohesion: 0.09
Nodes (42): QuizTakePage, OfflineBanner(), useOnlineStatus(), api, readingTime(), contentLanguage(), localizedArticle(), localizedCategory() (+34 more)

### Community 2 - "Icons.jsx"
Cohesion: 0.08
Nodes (30): NotificationsPage, AuthShell(), FEATURES, GuestSaveCta(), AcademicCap(), Bell(), BookOpen(), ChatBubble() (+22 more)

### Community 3 - "devDependencies"
Cohesion: 0.05
Nodes (41): autoprefixer, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, globals, jsdom, devDependencies (+33 more)

### Community 4 - "dependencies"
Cohesion: 0.05
Nodes (38): axios, dompurify, i18next, i18next-browser-languagedetector, idb, marked, dependencies, axios (+30 more)

### Community 5 - "api.js"
Cohesion: 0.10
Nodes (21): SsoCallbackPage, TutorPage, AuthProvider(), applyDirection(), initial, DEFAULT_LANGUAGE, normalizeLanguage(), RTL_LANGUAGES (+13 more)

### Community 6 - "ui.jsx"
Cohesion: 0.10
Nodes (26): DashboardPage, ProfilePage, ResetPasswordPage, GamificationSummary(), Eye(), EyeOff(), ORG_ROLE_STYLES, OrgRoleBadge() (+18 more)

### Community 7 - "ArticleEditorPage.jsx"
Cohesion: 0.13
Nodes (16): ArticleEditorPage, MediaEditorPage, ChevronLeft(), MediaPlayer(), renderMarkdown(), API_ORIGIN, resolveMediaUrl(), getEmbedInfo() (+8 more)

### Community 8 - "helpers.js"
Cohesion: 0.19
Nodes (11): API, apiGlob(), LIVE_ADMIN_EMAIL, LIVE_ADMIN_PASSWORD, LIVE_API, LIVE_ORG_SLUG, liveAuthHeaders(), loginLive() (+3 more)

### Community 9 - "Layout.jsx"
Cohesion: 0.15
Nodes (7): ArrowUp(), Moon(), Sun(), InstallPrompt(), OrgSwitcher(), QuotaBanner(), useDarkMode()

### Community 10 - "services.js"
Cohesion: 0.23
Nodes (11): AdminPage, EmailVerifyBanner(), AuthContext, auditService, authService, forumService, notificationService, notifyService (+3 more)

### Community 11 - "useAuth"
Cohesion: 0.24
Nodes (12): Layout(), ProtectedRoute(), mockedUseAuth, mockUser, useAuth(), useOrganization(), AdminPage(), ArticlesManagePage() (+4 more)

### Community 12 - "extractError"
Cohesion: 0.19
Nodes (11): AcceptInvitePage, ForgotPasswordPage, PushNotificationPrompt(), urlBase64ToUint8Array(), extractError(), AcceptInvitePage(), CategoriesManagePage(), slugify() (+3 more)

### Community 13 - "main.jsx"
Cohesion: 0.19
Nodes (6): App(), guard(), ErrorBoundary, queryClient, captureUiError(), initSentry()

### Community 14 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, baseUrl, checkJs, jsx, module, moduleResolution, target, types (+4 more)

### Community 15 - "OrganizationPage.jsx"
Cohesion: 0.22
Nodes (10): OrganizationPage, TabList(), TabPanel(), OrganizationProvider(), DEFAULT_PRIMARY_COLOR, LEGACY_BLUE_PRIMARY_COLORS, normalizePrimaryColor(), ORG_ROLES (+2 more)

### Community 16 - "Civic Education RSS — Frontend"
Cohesion: 0.22
Nodes (8): Civic Education RSS — Frontend, Deployment, Environment variables, Features, Local setup, Project structure, Requirements, Scripts

### Community 17 - "BillingPage.jsx"
Cohesion: 0.31
Nodes (6): BillingPage, UsageBar(), billingService, API_ORIGIN, BillingPage(), formatPrice()

### Community 18 - "QuizEditorPage.jsx"
Cohesion: 0.50
Nodes (7): QuizEditorPage, buildPayload(), emptyQuestion(), optionsArMismatch(), optionsFromText(), questionFromApi(), QuizEditorPage()

### Community 19 - "BookmarkButton.jsx"
Cohesion: 0.40
Nodes (4): BookmarkButton(), Bookmark(), BookmarkFilled(), bookmarkService

### Community 20 - "LanguageSwitcher.jsx"
Cohesion: 0.50
Nodes (3): LanguageSwitcher(), mockRefreshUser, mockUpdateProfile

### Community 21 - "vercel.json"
Cohesion: 0.50
Nodes (3): buildCommand, outputDirectory, rewrites

## Knowledge Gaps
- **102 isolated node(s):** `LIVE_ADMIN_EMAIL`, `LIVE_ADMIN_PASSWORD`, `LIVE_ORG_SLUG`, `TUTOR_DONE`, `target` (+97 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `extractError()` connect `extractError` to `App.jsx`, `ArticleDetailPage.jsx`, `Icons.jsx`, `api.js`, `ui.jsx`, `ArticleEditorPage.jsx`, `services.js`, `useAuth`, `OrganizationPage.jsx`, `BillingPage.jsx`, `QuizEditorPage.jsx`, `BookmarkButton.jsx`, `LanguageSwitcher.jsx`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `useAuth()` connect `useAuth` to `App.jsx`, `ArticleDetailPage.jsx`, `Icons.jsx`, `api.js`, `ui.jsx`, `Layout.jsx`, `services.js`, `extractError`, `OrganizationPage.jsx`, `BookmarkButton.jsx`, `LanguageSwitcher.jsx`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `devDependencies` connect `devDependencies` to `dependencies`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **What connects `LIVE_ADMIN_EMAIL`, `LIVE_ADMIN_PASSWORD`, `LIVE_ORG_SLUG` to the rest of the system?**
  _102 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `App.jsx` be split into smaller, more focused modules?**
  _Cohesion score 0.05390835579514825 - nodes in this community are weakly interconnected._
- **Should `ArticleDetailPage.jsx` be split into smaller, more focused modules?**
  _Cohesion score 0.09152542372881356 - nodes in this community are weakly interconnected._
- **Should `Icons.jsx` be split into smaller, more focused modules?**
  _Cohesion score 0.07529411764705882 - nodes in this community are weakly interconnected._