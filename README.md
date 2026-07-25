# Civic Education Platform

Full-stack civic education platform for South Sudan: Django REST API + React (Vite + Tailwind) PWA with multi-tenant orgs, Stripe billing, and bilingual EN/AR UI.

- **Backend** (`backend/`): Django REST Framework, JWT, PostgreSQL, Celery, Supabase Storage
- **Frontend** (`frontend/`): React 19 + Vite + Tailwind, offline-capable PWA — see [frontend/README.md](frontend/README.md)

**Local dev:** run the backend, then `cd frontend && npm install && npm run dev` (API default: `http://127.0.0.1:8000/api`).

**Production:** [docs/production-launch.md](docs/production-launch.md) · [docs/production-env-checklist.md](docs/production-env-checklist.md) · [docs/enterprise.md](docs/enterprise.md) · [docs/tutor-rag.md](docs/tutor-rag.md) · [docs/constitution-content.md](docs/constitution-content.md) · [docs/compliance-readiness.md](docs/compliance-readiness.md) · [docs/disaster-recovery.md](docs/disaster-recovery.md) · [docs/scaling.md](docs/scaling.md)

---

## Backend setup

### Requirements

- Python 3.11+
- PostgreSQL 14+
- Redis (optional locally — tasks run inline when `CELERY_TASK_ALWAYS_EAGER=True`)

### Local setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env         # DATABASE_URL, SECRET_KEY
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

- API docs: http://127.0.0.1:8000/api/docs/
- Health: http://127.0.0.1:8000/api/health/
- Readiness (DB + Redis): http://127.0.0.1:8000/api/ready/

### Default accounts (after `seed_data`)

| Account | Email | Password | Notes |
|---------|-------|----------|-------|
| Platform admin | `admin@civic-education.ss` | `AdminPass123!` | Cross-tenant ops only |
| Demo org | `platform-demo` | — | 3 articles, 1 quiz, 1 forum topic |

Org registration creates an **editor** platform role + **owner** org membership — not platform admin.

### Maintenance commands

```bash
python manage.py demote_legacy_org_admins --dry-run   # legacy org owners with platform admin role
python manage.py backfill_audit_orgs --dry-run        # audit logs missing organization
python manage.py smoke_check --base-url http://127.0.0.1:8000
python manage.py check_integrations          # verify Stripe, Celery, Anthropic, etc.
python manage.py check_integrations --strict
python loadtest/ci_gate.py --host http://127.0.0.1:8000   # Locust smoke (also runs in CI)
python scripts/generate_pwa_icons.py                  # regenerate frontend/public/icon-*.png
```

**Enterprise SSO:** set `OIDC_*` vars (see [production-env-checklist.md](docs/production-env-checklist.md#6-enterprise-sso--openid-connect-optional)). Login: `/api/auth/sso/login/?org=your-slug`.

### Tests

```bash
cd backend
pytest
```

### Background tasks (Celery)

Emails, notification fan-out, SMS, and certificate PDFs run as Celery tasks. In development they run inline (no broker). For async:

```bash
# set CELERY_TASK_ALWAYS_EAGER=False and CELERY_BROKER_URL in .env
celery -A config worker --loglevel=info   # Windows: --pool=solo or start-worker.cmd
```

### Load testing

```bash
locust -f loadtest/locustfile.py --host http://localhost:8000
```

See [docs/scaling.md](docs/scaling.md) for async architecture and SRS scale targets.

### AI tutor (RAG)

The AI civic tutor answers questions using **published articles and PDF attachments** (keyword retrieval + Claude). Learners see **source citations** in the UI.

- **Docs:** [docs/tutor-rag.md](docs/tutor-rag.md) (endpoints, streaming, admin usage)
- **Constitution setup:** [docs/constitution-content.md](docs/constitution-content.md) (seed assets + article editor)
- **Production:** set `ANTHROPIC_API_KEY` — see [production-env-checklist.md](docs/production-env-checklist.md)

Quick test after `seed_data`:

```bash
# Log in, then POST /api/tutor/chat/ with a constitutional question
# Or open http://localhost:5173/tutor in the frontend
```

### Project structure

```
backend/
├── apps/
│   ├── accounts/     # Auth, users, roles
│   ├── tenants/      # Organizations, memberships, invites
│   ├── billing/      # Stripe subscriptions
│   ├── learning/     # Articles, categories
│   ├── quizzes/      # Quizzes, certificates
│   ├── forum/        # Topics & comments
│   ├── notifications/# In-app, SMS, web push
│   ├── tutor/        # AI tutor (Anthropic + RAG/PDF grounding)
│   ├── gamification/ # XP, levels, badges
│   ├── engagement/   # Polls, petitions, campaigns
│   ├── analytics/    # Platform + org + personal dashboards
│   ├── audit/        # Activity logs (org-scoped)
│   └── core/         # Health, readiness, integration checks
└── config/           # Django settings
```

### Deployment (Render)

See [render.yaml](render.yaml). Copy env vars from [backend/.env.production.example](backend/.env.production.example).

## API reference

Hand-maintained overview: [docs/api.md](docs/api.md). Authoritative schema: `/api/docs/` (Swagger).

Testing: [docs/testing.md](docs/testing.md) — pytest, Vitest, mocked & live Playwright e2e.

Key doc pages:

| Topic | Doc |
|-------|-----|
| Tutor RAG + streaming | [docs/tutor-rag.md](docs/tutor-rag.md) |
| Constitution / PDF upload | [docs/constitution-content.md](docs/constitution-content.md) |
| Integration env vars | [docs/production-env-checklist.md](docs/production-env-checklist.md) |
