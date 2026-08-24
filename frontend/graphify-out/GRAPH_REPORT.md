# Graph Report - frontend  (2026-08-24)

## Corpus Check
- 144 files · ~85,221 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 572 nodes · 1673 edges · 29 communities
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 24 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0f7f6397`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- useAuth
- ProfilePage.jsx
- BillingPage.jsx
- devDependencies
- dependencies
- TutorPage.jsx
- ui.jsx
- ArticleDetailPage.jsx
- helpers.js
- Icons.jsx
- services.js
- App.jsx
- compilerOptions
- Civic Education RSS — Frontend
- extractError
- vercel.json

## God Nodes (most connected - your core abstractions)
1. `extractError()` - 65 edges
2. `useAuth()` - 53 edges
3. `formatDate()` - 37 edges
4. `Alert()` - 36 edges
5. `Spinner()` - 31 edges
6. `useOrganization()` - 30 edges
7. `queryKeys` - 30 edges
8. `PageHeader()` - 29 edges
9. `EmptyState()` - 18 edges
10. `normalizeLanguage()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `NewsEditorPage()` --calls--> `extractError()`  [EXTRACTED]
  src/pages/NewsEditorPage.jsx → src/lib/api.js
- `ResetPasswordPage()` --calls--> `extractError()`  [EXTRACTED]
  src/pages/ResetPasswordPage.jsx → src/lib/api.js
- `CertificatesPage()` --calls--> `formatDate()`  [EXTRACTED]
  src/pages/CertificatesPage.jsx → src/lib/format.js
- `NotificationsPage()` --calls--> `formatDate()`  [EXTRACTED]
  src/pages/NotificationsPage.jsx → src/lib/format.js
- `ResultsPage()` --calls--> `formatDate()`  [EXTRACTED]
  src/pages/ResultsPage.jsx → src/lib/format.js

## Import Cycles
- None detected.

## Communities (29 total, 0 thin omitted)

### Community 0 - "useAuth"
Cohesion: 0.09
Nodes (51): AcceptInvitePage, CategoriesManagePage, NewsEditorPage, Breadcrumb(), CLAIM_ALERT, CLAIM_STYLES, claimAlertKind(), ClaimBadge() (+43 more)

### Community 1 - "ProfilePage.jsx"
Cohesion: 0.11
Nodes (32): ProfilePage, QuizTakePage, OfflineBanner(), OrgRoleBadge(), RoleBadge(), useOnlineStatus(), api, fetchOrCache() (+24 more)

### Community 2 - "BillingPage.jsx"
Cohesion: 0.07
Nodes (25): BillingPage, ResetPasswordPage, AuthShell(), PlatformLogo(), PasswordInput(), UsageBar(), PLATFORM_LOGO_ALT, PLATFORM_LOGO_URL (+17 more)

### Community 3 - "devDependencies"
Cohesion: 0.05
Nodes (41): autoprefixer, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, globals, jsdom, devDependencies (+33 more)

### Community 4 - "dependencies"
Cohesion: 0.05
Nodes (38): axios, dompurify, i18next, i18next-browser-languagedetector, idb, marked, dependencies, axios (+30 more)

### Community 5 - "TutorPage.jsx"
Cohesion: 0.10
Nodes (22): SsoCallbackPage, TutorPage, LanguageSwitcher(), mockRefreshUser, mockUpdateProfile, AuthProvider(), applyDirection(), initial (+14 more)

### Community 6 - "ui.jsx"
Cohesion: 0.09
Nodes (24): CertificatesPage, DashboardPage, ResultsPage, GamificationSummary(), EyeOff(), Trophy(), Pagination(), ORG_ROLE_STYLES (+16 more)

### Community 7 - "ArticleDetailPage.jsx"
Cohesion: 0.08
Nodes (34): ArticleDetailPage, ArticleEditorPage, ArticlesPage, QuizzesPage, SearchPage, GuestSaveCta(), MediaPlayer(), CardSkeleton() (+26 more)

### Community 8 - "helpers.js"
Cohesion: 0.19
Nodes (11): API, apiGlob(), LIVE_ADMIN_EMAIL, LIVE_ADMIN_PASSWORD, LIVE_API, LIVE_ORG_SLUG, liveAuthHeaders(), loginLive() (+3 more)

### Community 9 - "Icons.jsx"
Cohesion: 0.09
Nodes (26): NotificationsPage, FEATURES, AcademicCap(), ArrowUp(), Bell(), BookOpen(), ChatBubble(), ChevronRight() (+18 more)

### Community 10 - "services.js"
Cohesion: 0.16
Nodes (16): TabList(), TabPanel(), analyticsService, auditService, awarenessService, billingService, forumService, notificationService (+8 more)

### Community 13 - "App.jsx"
Cohesion: 0.06
Nodes (24): AdminPage, App(), ArticlesManagePage, AwarenessPage, ContactPage, ForumPage, guard(), MediaDetailPage (+16 more)

### Community 14 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, baseUrl, checkJs, jsx, module, moduleResolution, target, types (+4 more)

### Community 16 - "Civic Education RSS — Frontend"
Cohesion: 0.22
Nodes (8): Civic Education RSS — Frontend, Deployment, Environment variables, Features, Local setup, Project structure, Requirements, Scripts

### Community 18 - "extractError"
Cohesion: 0.07
Nodes (30): EngagementPage, ForgotPasswordPage, MediaEditorPage, QuizEditorPage, SavedPage, BookmarkButton(), EmailVerifyBanner(), Bookmark() (+22 more)

### Community 21 - "vercel.json"
Cohesion: 0.50
Nodes (3): buildCommand, outputDirectory, rewrites

## Knowledge Gaps
- **104 isolated node(s):** `LIVE_ADMIN_EMAIL`, `LIVE_ADMIN_PASSWORD`, `LIVE_ORG_SLUG`, `TUTOR_DONE`, `target` (+99 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `extractError()` connect `extractError` to `useAuth`, `ProfilePage.jsx`, `BillingPage.jsx`, `TutorPage.jsx`, `ui.jsx`, `ArticleDetailPage.jsx`, `Icons.jsx`, `services.js`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `useAuth()` connect `useAuth` to `ProfilePage.jsx`, `BillingPage.jsx`, `TutorPage.jsx`, `ArticleDetailPage.jsx`, `Icons.jsx`, `services.js`, `extractError`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `devDependencies` connect `devDependencies` to `dependencies`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **What connects `LIVE_ADMIN_EMAIL`, `LIVE_ADMIN_PASSWORD`, `LIVE_ORG_SLUG` to the rest of the system?**
  _104 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `useAuth` be split into smaller, more focused modules?**
  _Cohesion score 0.08936936936936937 - nodes in this community are weakly interconnected._
- **Should `ProfilePage.jsx` be split into smaller, more focused modules?**
  _Cohesion score 0.10808080808080808 - nodes in this community are weakly interconnected._
- **Should `BillingPage.jsx` be split into smaller, more focused modules?**
  _Cohesion score 0.07419712070874862 - nodes in this community are weakly interconnected._