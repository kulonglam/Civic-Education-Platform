# Civic Education Platform — Frontend

React 19 + Vite + Tailwind CSS PWA for the Civic Education Platform. Talks to the Django REST API ([../backend](../backend)).

## Requirements

- Node.js 18+
- Backend API running (default `http://127.0.0.1:8000/api`)

## Local setup

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

App: http://localhost:5173

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Dev server |
| `npm run build` | Production build (`dist/`) |
| `npm run preview` | Preview production build |
| `npm test` | Vitest unit tests |
| `npm run lint` | ESLint |

## Features

- JWT auth with token refresh (`src/lib/api.js`)
- Multi-tenant org switcher + invites (`OrganizationContext`)
- Role-based routes: citizen, moderator, editor, platform admin
- Articles (markdown), quizzes, certificates, offline article/quiz cache
- Forum with moderation queue
- AI tutor, billing (Stripe checkout), org SMS alerts
- In-app notifications + optional web push (VAPID)
- Bilingual EN/AR with RTL (`react-i18next`, localized API content)

## Environment variables

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Backend API base (e.g. `http://127.0.0.1:8000/api`) |
| `VITE_DEFAULT_TENANT_SLUG` | Default org slug for citizens (`platform-demo`) |
| `VITE_VAPID_PUBLIC_KEY` | Web push (must match backend `VAPID_PUBLIC_KEY`) |
| `VITE_SENTRY_DSN` | Optional error tracking |

Production template: [.env.production.example](.env.production.example)

## Project structure

```
src/
├── components/      # Layout, PWA prompts, UI primitives
├── context/         # Auth + organization state
├── i18n/            # EN/AR translations
├── lib/             # API client, offline sync, markdown, i18n content
├── pages/           # Route pages
└── hooks/           # Shared hooks
```

## Deployment

Static build (`npm run build`). Set `VITE_*` vars at build time.

- **Render:** see root [render.yaml](../render.yaml) (`civic-education-web`)
- **Vercel:** `vercel.json` SPA rewrites; set `VITE_API_BASE_URL` to your API URL
