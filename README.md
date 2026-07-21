# Civic Education Platform

Full-stack civic education platform for South Sudan: Django REST API + React (Vite + Tailwind) PWA with multi-tenant orgs, Stripe billing, and bilingual EN/AR UI.

- **Backend** (`backend/`): Django REST Framework, JWT, PostgreSQL, Celery, Supabase Storage
- **Frontend** (`frontend/`): React 19 + Vite + Tailwind, offline-capable PWA — see [frontend/README.md](frontend/README.md)

**Local dev:** run the backend, then `cd frontend && npm install && npm run dev` (API default: `http://127.0.0.1:8000/api`).

**Production:** [docs/production-launch.md](docs/production-launch.md) · [docs/production-env-checklist.md](docs/production-env-checklist.md) · [docs/enterprise.md](docs/enterprise.md) · [docs/compliance-readiness.md](docs/compliance-readiness.md) · [docs/disaster-recovery.md](docs/disaster-recovery.md) · [docs/scaling.md](docs/scaling.md)

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
│   ├── tutor/        # AI tutor (Anthropic)
│   ├── analytics/    # Platform + org dashboards
│   └── audit/        # Activity logs (org-scoped)
└── config/           # Django settings
```

### Deployment (Render)

See [render.yaml](render.yaml). Copy env vars from [backend/.env.production.example](backend/.env.production.example).

## API reference

Hand-maintained overview: [docs/api.md](docs/api.md). Authoritative schema: `/api/docs/` (Swagger).
