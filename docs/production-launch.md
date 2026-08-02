# Production launch guide

Step-by-step checklist to take the Civic Education Platform from local development to a live production deployment.

## Architecture

| Component | Role |
|-----------|------|
| **Web API** | Django + Gunicorn (`/api/*`) |
| **Worker** | Celery (notifications, email, certificate PDFs) |
| **Redis** | Celery broker + cache (readiness probe) |
| **PostgreSQL** | Primary database (+ optional read replica via `DATABASE_URL_REPLICA`) |
| **Static frontend** | Vite build served from CDN/static host |
| **Supabase Storage** | File uploads and certificate PDFs |
| **Stripe** | Subscription billing (required in production) |

## Pre-launch checklist

### 1. Domain and TLS

- [ ] Register API domain (e.g. `api.yourdomain.com`)
- [ ] Register app domain (e.g. `app.yourdomain.com`)
- [ ] Enable HTTPS on both (Render/Vercel/Cloudflare handle this automatically)

### 2. Backend secrets

Copy [backend/.env.production.example](../backend/.env.production.example) and set every value:

- [ ] `SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"`
- [ ] `ALLOWED_HOSTS` — your API domain(s); on Render, `RENDER_EXTERNAL_HOSTNAME` is merged automatically
- [ ] `CORS_ALLOWED_ORIGINS` — your frontend HTTPS URL
- [ ] `DATABASE_URL` — managed PostgreSQL connection string
- [ ] `FRONTEND_URL` — frontend HTTPS URL
- [ ] `CELERY_BROKER_URL` + `REDIS_URL` — managed Redis
- [ ] `BILLING_PROVIDER=stripe` with live Stripe keys and price IDs
- [ ] `SUPABASE_URL` + `SUPABASE_KEY` for file storage
- [ ] SMTP credentials for password reset and verification emails
- [ ] Optional: `SENTRY_DSN` for error tracking

Validate before deploy:

```bash
cd backend
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py check --deploy
```

Production settings **fail on boot** if `BILLING_PROVIDER=dummy`, `SECRET_KEY` is insecure, or Redis/CORS/hosts are missing.

**Integrations (SMS, web push, Anthropic, Stripe, Celery):** see [production-env-checklist.md](production-env-checklist.md) for variable names, service parity (web vs worker), and verification steps.

### 3. Database

```bash
python manage.py migrate
python manage.py seed_data   # optional: demo org + admin
```

Create a real superuser for Django admin:

```bash
python manage.py createsuperuser
```

### 4. Stripe setup

1. Create Products/Prices in Stripe Dashboard for `pro` and `enterprise` plans.
2. Set `STRIPE_PRICE_PRO` and `STRIPE_PRICE_ENTERPRISE` to the Price IDs.
3. Add webhook endpoint: `https://api.yourdomain.com/api/billing/webhook/`
4. Subscribe to: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
5. Copy webhook signing secret to `STRIPE_WEBHOOK_SECRET`.

### 5. Frontend build

```bash
cd frontend
cp .env.production.example .env.production
# Set VITE_API_BASE_URL=https://api.yourdomain.com/api
npm ci
npm run build
```

Deploy the `frontend/dist` folder to your static host (Render Static Site, Netlify, Vercel, S3+CloudFront).

### 6. Render (included blueprint)

The repo includes [render.yaml](../render.yaml) for API + worker + Redis + Postgres + daily backup + weekly audit purge + static frontend. After connecting the repo:

1. Set sync=false env vars in the Render dashboard (`CORS_ALLOWED_ORIGINS`, Stripe, Supabase, email, Sentry). `ALLOWED_HOSTS` can list custom API domains; the service’s `*.onrender.com` hostname is picked up via `RENDER_EXTERNAL_HOSTNAME` automatically.
2. Attach custom domains: API (`api.yourdomain.com`) on the web service and app (`app.yourdomain.com`) on the static site — HTTPS is automatic.
3. Configure **Supabase Storage** (or S3-compatible): set `SUPABASE_URL` + `SUPABASE_KEY` on both web and worker so certificate PDFs and article attachments upload correctly.
4. Confirm worker and web services share the same `SECRET_KEY` and `DATABASE_URL`.
5. Optional: set `VITE_SENTRY_DSN` on the static site (build-time) and `SENTRY_DSN` on the API.

Build command runs migrations automatically:

```
pip install -r backend/requirements.txt && cd backend && python manage.py migrate && python manage.py collectstatic --noinput
```

**Enterprise SSO:** prefer per-organization IdP settings in Organization → SSO (Enterprise plan). Global `OIDC_*` env vars remain as a platform-wide fallback.
### 7. Health checks

Configure your load balancer or platform probes:

| Endpoint | Purpose |
|----------|---------|
| `GET /api/health/` | Liveness — process is up |
| `GET /api/ready/` | Readiness — PostgreSQL + Redis reachable |

### 8. Post-deploy smoke test

- [ ] Register a new organization at the frontend URL
- [ ] Log in, switch org (if multi-org), create a draft article
- [ ] Take a quiz and confirm certificate flow
- [ ] Upgrade plan via Stripe checkout (test mode first, then live)
- [ ] Confirm webhook updates subscription status
- [ ] Trigger password reset email

### 9. Security hardening (included)

- Tenant middleware validates `X-Tenant-Slug` against JWT membership
- Mutating API endpoints require `IsOrgMember`
- Production blocks dummy billing, insecure secrets, and eager Celery
- HSTS, secure cookies, SSL redirect enabled in production settings

### 10. Ongoing operations

- Run Celery worker alongside the web process (see `render.yaml` worker service)
- Monitor `/api/ready/` and Sentry (if configured)
- Daily DB backups via `python manage.py backup_database` (Render cron in `render.yaml`, 03:00 UTC)
- Rotate `SECRET_KEY` and Stripe keys on a documented schedule

### 11. Organization invites

Org admins can invite colleagues from **Organization → Invite**:

- **Existing users** are added immediately and notified by email.
- **New users** receive an email with a link to `/invite/{token}` — they can register with the invited email or log in and accept.

API endpoints:

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/organization/members/invite/` | Send invite or add existing member |
| `GET` | `/api/organization/invites/` | List pending invites (admin) |
| `DELETE` | `/api/organization/invites/{id}/` | Revoke pending invite |
| `GET` | `/api/organization/invites/preview/{token}/` | Public invite details |
| `POST` | `/api/organization/invites/accept/{token}/` | Accept while logged in |

Registration accepts `invite_token` to join the org instead of creating a new one.

### 12. Error monitoring (Sentry)

Backend (optional): set `SENTRY_DSN` and `SENTRY_ENVIRONMENT` — Django + Celery integrations are enabled automatically.

Frontend (optional): set at **build time**:

```
VITE_SENTRY_DSN=https://...@sentry.io/...
VITE_SENTRY_ENVIRONMENT=production
```

### 13. Database backups

Manual backup (requires `pg_dump` on PATH):

```bash
cd backend
python manage.py backup_database --output-dir ./backups --retain 14
```

Environment variables:

| Variable | Purpose |
|----------|---------|
| `BACKUP_DIR` | Output directory (default: `./backups`) |
| `BACKUP_RETAIN_DAYS` | Auto-delete backups older than N days |

Render: the `civic-education-backup` cron job in `render.yaml` runs daily at 03:00 UTC. Mount persistent disk at `/var/data/backups` or sync to object storage for off-site retention.

Audit log retention: the `civic-education-audit-purge` cron runs weekly and executes `python manage.py purge_audit_logs` using each org's `audit_retention_days`.

#### Restore runbook

1. **Stop writers** — scale down web/worker (or put maintenance mode) so no new writes race the restore.
2. **Identify backup** — pick the `.sql` / `.dump` file from `BACKUP_DIR` (or object storage) for the target time.
3. **Restore PostgreSQL** (example with custom-format dump from `pg_dump -Fc`):

   ```bash
   pg_restore --clean --if-exists --no-owner --dbname="$DATABASE_URL" /path/to/backup.dump
   ```

   For plain SQL dumps: `psql "$DATABASE_URL" < backup.sql`
4. **Media** — if Supabase/S3 holds PDFs and avatars, restore the bucket snapshot from the same window (DB alone is not enough for certificates).
5. **Verify** — hit `GET /api/ready/`, log in as platform admin, spot-check org membership and a recent certificate download.
6. **Scale up** — restart worker, then web; confirm Sentry is quiet and Stripe webhooks resume.

Document the restore time and backup filename in your incident notes.

### 14. E2E testing

**Mocked (fast, default CI):** `npm run test:e2e`

**Live API (requires seeded backend + Postgres):**

```bash
# Terminal 1 — backend with Postgres
cd backend && python manage.py migrate && python manage.py seed_data && python manage.py runserver

# Terminal 2 — frontend live E2E
cd frontend
# PowerShell:
$env:E2E_LIVE=1; npm run test:e2e:live
```

CI runs both mocked and live E2E (live job uses Postgres service + `seed_data`).

## Local production simulation

To test production settings locally (without deploying):

```bash
cd backend
set DJANGO_SETTINGS_MODULE=config.settings.production
set SECRET_KEY=local-prod-test-secret-not-for-real-use-abc123xyz
set ALLOWED_HOSTS=127.0.0.1
set CORS_ALLOWED_ORIGINS=https://127.0.0.1:5173
set BILLING_PROVIDER=stripe
set STRIPE_SECRET_KEY=sk_test_xxx
set STRIPE_WEBHOOK_SECRET=whsec_xxx
set CELERY_BROKER_URL=redis://localhost:6379/0
python manage.py check --deploy
```

## Support

- API reference: `/api/docs/` (disable public schema in production if desired)
- Scaling notes: [scaling.md](scaling.md)
