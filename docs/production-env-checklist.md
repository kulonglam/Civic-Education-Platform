# Production environment checklist — integrations

Use this alongside [production-launch.md](production-launch.md). Copy templates from:

- Backend: [backend/.env.production.example](../backend/.env.production.example)
- Frontend: [frontend/.env.production.example](../frontend/.env.production.example)

Production Django settings **require** Stripe and Celery/Redis. SMS, web push, and Anthropic are optional but must be configured for those features to work in production (otherwise they silently fall back to dummy/stub behavior).

---

## Quick reference

| Feature | Required in prod? | Backend vars | Frontend vars | Worker needs same vars? |
|---------|-------------------|--------------|---------------|-------------------------|
| **Stripe billing** | Yes | `BILLING_PROVIDER`, `STRIPE_*` | — | No |
| **Celery + Redis** | Yes | `CELERY_BROKER_URL`, `REDIS_URL`, `CELERY_TASK_ALWAYS_EAGER=False` | — | Yes (worker service) |
| **SMS alerts** | No (Pro/Enterprise feature) | `SMS_PROVIDER`, `AT_*` | — | Yes (SMS tasks) |
| **Web push** | No | `VAPID_*` | `VITE_VAPID_PUBLIC_KEY` | Yes (push in notify tasks) |
| **AI tutor** | No | `ANTHROPIC_*` | — | No (sync API) |
| **Enterprise SSO** | No (Enterprise plan) | `OIDC_*`, `API_BASE_URL` | — | Web only |

---

## 1. Celery + Redis (required)

Background work depends on a running **Celery worker** and **Redis**:

- Email verification & password reset
- Notification fan-out (in-app announcements to all members)
- SMS queue delivery
- Certificate PDF generation

### Backend environment

```env
CELERY_BROKER_URL=redis://:password@your-redis-host:6379/0
REDIS_URL=redis://:password@your-redis-host:6379/0
CELERY_TASK_ALWAYS_EAGER=False
```

### Deploy checklist

- [ ] Redis instance provisioned (Render Redis, ElastiCache, Upstash, etc.)
- [ ] `CELERY_BROKER_URL` set on **web** and **worker** services (same value)
- [ ] `REDIS_URL` set (used by `/api/ready/` health check)
- [ ] `CELERY_TASK_ALWAYS_EAGER=False` on web and worker
- [ ] Worker process running: `celery -A config worker --loglevel=info`
- [ ] `GET /api/ready/` returns OK (PostgreSQL + Redis)

### Verify

```bash
# After deploy — readiness should pass
curl https://api.yourdomain.com/api/ready/

# Trigger async work (register user → verification email should send via worker)
# Check worker logs for task execution
```

### Render

The repo [render.yaml](../render.yaml) defines `civic-education-worker` and `civic-education-redis`. Ensure the worker service is deployed and not suspended.

---

## 2. Stripe billing (required)

Production boot **fails** if `BILLING_PROVIDER=dummy`.

### Backend environment

```env
BILLING_PROVIDER=stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_ENTERPRISE=price_...
FRONTEND_URL=https://app.yourdomain.com
```

### Stripe Dashboard checklist

- [ ] Create **Products/Prices** for Pro and Enterprise (match plan codes in `seed_data`)
- [ ] Copy **live** Price IDs → `STRIPE_PRICE_PRO`, `STRIPE_PRICE_ENTERPRISE`
- [ ] Webhook endpoint: `https://api.yourdomain.com/api/billing/webhook/`
- [ ] Subscribe to events:
  - `checkout.session.completed`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
- [ ] Copy signing secret → `STRIPE_WEBHOOK_SECRET`
- [ ] Test checkout in **test mode** first, then switch to live keys

### Verify

- [ ] Org admin → Billing → upgrade opens Stripe Checkout
- [ ] After payment, subscription status updates (webhook received)
- [ ] Billing portal opens from “Manage billing”
- [ ] Downgrade/cancel reflects in app after webhook

---

## 3. SMS — Africa's Talking (optional)

Used for: org SMS broadcasts, targeted SMS, phone OTP (verify + password reset).

If unset, `SMS_PROVIDER` stays `dummy` — messages are logged but not delivered.

### Backend environment

```env
SMS_PROVIDER=africastalking
AT_USERNAME=your-at-username
AT_API_KEY=your-at-api-key
AT_SENDER_ID=YOUR_SENDER
```

| Variable | Where to get it |
|----------|-----------------|
| `AT_USERNAME` | Africa's Talking dashboard → account username (use `sandbox` for testing) |
| `AT_API_KEY` | Dashboard → Settings → API Key |
| `AT_SENDER_ID` | Approved alphanumeric sender ID (or leave blank in sandbox) |

### Checklist

- [ ] Africa's Talking account created
- [ ] Sender ID approved (production) or sandbox tested
- [ ] Vars set on **web** and **Celery worker** (SMS sends via `send_sms_task`)
- [ ] Org on **Pro or Enterprise** plan (`sms_alerts` feature flag)
- [ ] Member phone numbers in E.164 South Sudan format (`+211…`)

### Verify

- [ ] Organization → SMS alerts → send test broadcast
- [ ] Check `GET /api/notify/history/` for `sent` status
- [ ] Profile → phone verify OTP received
- [ ] Worker logs show Africa's Talking response (not `[dummy-sms]`)

---

## 4. Web push — VAPID (optional)

Used for: browser push when in-app notifications are created.

If VAPID keys are missing, push is skipped silently. The frontend install prompt only appears when `VITE_VAPID_PUBLIC_KEY` is set.

### Generate keys

```bash
npx web-push generate-vapid-keys
```

### Backend environment

```env
VAPID_PUBLIC_KEY=BNx...   # public key from command above
VAPID_PRIVATE_KEY=abc...  # private key — keep secret
VAPID_ADMIN_EMAIL=mailto:admin@yourdomain.com
```

### Frontend environment (build time)

```env
VITE_VAPID_PUBLIC_KEY=BNx...   # must match backend VAPID_PUBLIC_KEY exactly
```

Set in `frontend/.env.production` before `npm run build`, or in your static host build env (Render `civic-education-web`).

### Checklist

- [ ] VAPID key pair generated once; store private key securely
- [ ] Backend `VAPID_PUBLIC_KEY` = frontend `VITE_VAPID_PUBLIC_KEY`
- [ ] `VAPID_ADMIN_EMAIL` is a valid `mailto:` contact (Web Push spec)
- [ ] HTTPS enabled (required for service workers)
- [ ] PWA/service worker deployed (`npm run build` includes `push-sw.js`)

### Verify

- [ ] Log in → browser prompts to enable notifications (if permission not set)
- [ ] Trigger an in-app announcement to your org → push notification appears
- [ ] Backend worker logs show push delivery (or 410 cleanup for stale subscriptions)

---

## 5. AI tutor — Anthropic (optional)

Used for: `/api/tutor/chat/` Claude responses.

If `ANTHROPIC_API_KEY` is blank, the API returns a **development stub** message — not suitable for production learners.

### Backend environment

```env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-20250514
ANTHROPIC_MAX_TOKENS=1024
```

### Checklist

- [ ] Anthropic API key created with usage limits/budget alerts
- [ ] Key set on **web** service only (tutor runs synchronously in request)
- [ ] Plan quotas configured (`tutor_daily_messages` in billing plan features)
- [ ] Monitor token usage via Anthropic dashboard

### Verify

- [ ] Tutor page → ask a civic question → real Claude reply (not “development response”)
- [ ] Daily usage counter increments (`GET /api/tutor/usage/`)
- [ ] Free-plan limit enforced when quota exceeded

---

## 6. Enterprise SSO — OpenID Connect (optional)

Requires **Enterprise** plan (`sso` feature flag). Without OIDC env vars, status endpoints report `configured: false`.

### Backend environment

```env
API_BASE_URL=https://api.yourdomain.com
OIDC_ISSUER=https://your-idp.example.com
OIDC_CLIENT_ID=...
OIDC_CLIENT_SECRET=...
OIDC_REDIRECT_URI=https://api.yourdomain.com/api/auth/sso/callback/
OIDC_SCOPES=openid email profile
```

### Checklist

- [ ] IdP application registered with redirect URI above
- [ ] Enterprise subscription active for the organization
- [ ] `GET /api/auth/sso/status/?org=your-org-slug` returns `configured: true`
- [ ] Login page shows **Sign in with SSO** for org members
- [ ] Callback redirects to `{FRONTEND_URL}/sso/callback` with JWT tokens

---

## 7. Pre-flight validation

```bash
cd backend
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py check --deploy
```

Expected failures if misconfigured:

| Error | Fix |
|-------|-----|
| `BILLING_PROVIDER must be "stripe"` | Set `BILLING_PROVIDER=stripe` |
| `CELERY_BROKER_URL is required` | Set Redis URL |
| Insecure `SECRET_KEY` | Generate new secret |

### Full smoke test (integrations)

- [ ] **Celery**: registration email arrives (worker processing)
- [ ] **Stripe**: checkout + webhook updates plan
- [ ] **SMS**: org broadcast queues and delivers (Pro plan)
- [ ] **Push**: announcement triggers browser notification
- [ ] **Tutor**: non-stub AI response

Automated HTTP smoke (after deploy):

```bash
cd backend
python manage.py smoke_check --base-url https://api.yourdomain.com --tenant-slug platform-demo
```

---

## 8. Service env parity (Render / Docker)

Ensure these vars are identical on **web** and **worker** where noted:

| Variable | Web | Worker |
|----------|-----|--------|
| `SECRET_KEY` | ✓ | ✓ |
| `DATABASE_URL` | ✓ | ✓ |
| `CELERY_BROKER_URL` | ✓ | ✓ |
| `CELERY_TASK_ALWAYS_EAGER=False` | ✓ | ✓ |
| `SUPABASE_URL` / `SUPABASE_KEY` | ✓ | ✓ (certificate PDFs) |
| `SMS_PROVIDER`, `AT_*` | ✓ | ✓ |
| `VAPID_*` | ✓ | ✓ |
| `STRIPE_*` | ✓ | — |
| `ANTHROPIC_*` | ✓ | — |
| Email SMTP vars | ✓ | ✓ |

Frontend build (separate static deploy):

| Variable | Required |
|----------|----------|
| `VITE_API_BASE_URL` | Yes |
| `VITE_DEFAULT_TENANT_SLUG` | Yes (usually `platform-demo`) |
| `VITE_VAPID_PUBLIC_KEY` | For push |
| `VITE_SENTRY_DSN` | Optional |
