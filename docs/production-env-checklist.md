# Production environment checklist — integrations

Use this alongside [production-launch.md](production-launch.md) and the ordered walkthrough [production-credentials.md](production-credentials.md). Copy templates from:

- Backend: [backend/.env.production.example](../backend/.env.production.example)
- Frontend: [frontend/.env.production.example](../frontend/.env.production.example)

Production Django settings require Celery/Redis. Billing in East Africa is **invoice / card upgrade** (`BILLING_PROVIDER=dummy`); Stripe is optional and unused when dummy billing is allowed. SMS, WhatsApp, and the AI tutor are optional but must be configured for those features to work in production (otherwise they silently fall back to dummy/stub behavior).

---

## Quick reference

| Feature | Required in prod? | Backend vars | Frontend vars | Worker needs same vars? |
|---------|-------------------|--------------|---------------|-------------------------|
| **Billing (invoice / dummy)** | Yes (this region) | `BILLING_PROVIDER=dummy`, `ALLOW_DUMMY_BILLING_IN_PRODUCTION` | — | No |
| **Celery + Redis** | Yes | `CELERY_BROKER_URL`, `REDIS_URL`, `CELERY_TASK_ALWAYS_EAGER=False` | — | Yes (worker service) |
| **SMS alerts** | No (Pro/Enterprise feature) | `SMS_PROVIDER`, `AT_*` | — | Yes (SMS tasks) |
| **WhatsApp alerts** | No (same Pro/Enterprise messaging feature) | `WHATSAPP_*` | — | Yes (WhatsApp tasks) |
| **Web push** | No | `VAPID_*` | `VITE_VAPID_PUBLIC_KEY` | Yes (push in notify tasks) |
| **AI tutor** | No | `TUTOR_PROVIDER`, `ANTHROPIC_*` or `OPENAI_*` | — | No (sync API) |
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

# Full integration report (platform admin JWT)
curl -H "Authorization: Bearer $TOKEN" https://api.yourdomain.com/api/integrations/status/

# CLI on web or worker container
cd backend
python manage.py check_integrations
python manage.py check_integrations --strict   # exit 1 if required integrations missing
python manage.py check_integrations --json
```

### Render

The repo [render.yaml](../render.yaml) defines `civic-education-worker` and `civic-education-redis`. Ensure the worker service is deployed and not suspended.

---

## 2. Stripe billing (required for paid SaaS)

Production boot **fails** if `BILLING_PROVIDER=dummy` unless you explicitly opt out of payments (see **2b** below).

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

## 2b. No Stripe / unsupported country (e.g. Uganda)

Stripe does not support merchant accounts in every country. For **civic education deployments** where you do not collect subscription payments online:

```env
BILLING_PROVIDER=dummy
ALLOW_DUMMY_BILLING_IN_PRODUCTION=True
```

- No `STRIPE_*` variables required — the API will boot without them.
- Checkout of **paid** plans returns **403**. Super Admins assign Pro/Enterprise in Admin → Organizations (or `POST /api/organization/platform/orgs/<uuid>/plan/`) after invoice or card upgrade.
- Free (zero-price) plans can still be selected in-app.
- Do **not** expect instant self-upgrade to Pro on dummy billing — that path is locked so public sign-ups cannot grant themselves paid entitlements.

**Africa payment providers (future integration, not built yet):**

| Provider | Uganda support | Notes |
|----------|----------------|-------|
| Flutterwave | Yes | Cards, mobile money |
| Pesapal | Yes | East Africa focus |
| Paystack | Limited | Mainly NG/GH/SA |

Paid self-serve checkout is locked on dummy billing. Assign paid plans only after invoice or card upgrade. Flutterwave / Pesapal would be a future `BILLING_PROVIDER`, not a reason to re-enable dummy self-upgrade.

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
- [ ] Member phone numbers in E.164 Uganda format (`+256…`)

### Verify

- [ ] Organization → SMS alerts → send test broadcast
- [ ] Check `GET /api/notify/history/` for `sent` status
- [ ] Profile → phone verify OTP received
- [ ] Worker logs show Africa's Talking response (not `[dummy-sms]`)

---

## 3b. WhatsApp Cloud API (optional)

Used for: org WhatsApp broadcasts, inbound webhook auto-replies, notification fan-out when a learner opts in. Share-to-WhatsApp links (`wa.me`) work without credentials.

If unset, `WHATSAPP_PROVIDER` stays `dummy` — outbound messages are logged, not delivered to Meta.

```env
WHATSAPP_PROVIDER=meta
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_VERIFY_TOKEN=
WHATSAPP_APP_SECRET=
WHATSAPP_DISPLAY_NUMBER=+256772000000
WHATSAPP_TEMPLATE_NAME=civic_alert
WHATSAPP_TEMPLATE_LANG=en
WHATSAPP_TEMPLATE_BODY_VARS=1
```

Approve a Meta template whose body has `{{1}}` (the alert text). Without `WHATSAPP_TEMPLATE_NAME`, sends are session text only (24-hour window). Point Meta's webhook to `POST /api/notify/whatsapp/webhook/` (and the GET verify handshake). Org admins send from Organization → WhatsApp alerts on a Pro/Enterprise plan (`sms_alerts`).

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

## 5. AI tutor (optional)

Used for: `/api/tutor/chat/` replies and automatic English/Arabic article translation on save.

`TUTOR_PROVIDER` selects the backend. The default `auto` uses Anthropic when keyed, otherwise an OpenAI-compatible endpoint, otherwise an offline **development stub** — the stub is not suitable for production learners. Article translation skips entirely when the stub is active (it never writes the canned reply into article fields).

| `TUTOR_PROVIDER` | Backend | Needs |
| --- | --- | --- |
| `auto` (default) | first configured of the below | — |
| `anthropic` | Claude | `ANTHROPIC_API_KEY` |
| `openai` | any OpenAI-compatible endpoint | `OPENAI_API_KEY` or `OPENAI_BASE_URL` |
| `stub` | offline canned reply | — |

Optional translation knobs (defaults are fine): `TRANSLATION_ENABLED`, `TRANSLATION_MAX_TOKENS` (4096), `TRANSLATION_CHUNK_CHARS` (3000). Backfill existing articles with `python manage.py translate_missing`.

| `TUTOR_PROVIDER` | Backend | Needs |
| --- | --- | --- |
| `auto` (default) | first configured of the below | — |
| `anthropic` | Claude | `ANTHROPIC_API_KEY` |
| `openai` | any OpenAI-compatible endpoint | `OPENAI_API_KEY` or `OPENAI_BASE_URL` |
| `stub` | offline canned reply | — |

### Backend environment

```env
TUTOR_PROVIDER=auto

# Option A — Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-20250514
ANTHROPIC_MAX_TOKENS=1024

# Option B — OpenAI-compatible (OpenAI, OpenRouter, Groq, Together, Ollama)
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=            # blank for OpenAI itself
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=1024
```

### Free option on Render ($0 ongoing)

OpenAI’s own API is billed. Ollama cannot run on Render free/starter. Use Groq’s OpenAI-compatible free tier:

```env
TUTOR_PROVIDER=openai
OPENAI_API_KEY=gsk_...
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.1-8b-instant
```

Create the key at https://console.groq.com. Leave `ANTHROPIC_API_KEY` blank. Restart the web service after saving.

### Free option for local testing

Run a local model instead of paying for tokens. Install [Ollama](https://ollama.com), then:

```bash
ollama pull llama3.1
ollama serve
```

```env
TUTOR_PROVIDER=openai
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.1
```

No API key is needed — the provider sends a placeholder key that local runtimes ignore. This only works where the backend can reach the Ollama host, so it suits local development rather than Render.

### Checklist

- [ ] Provider key created with usage limits/budget alerts
- [ ] Key set on **web** service only (tutor runs synchronously in request)
- [ ] Plan quotas configured (`tutor_daily_messages` in billing plan features)
- [ ] Monitor token usage in the provider dashboard

### Verify

- [ ] `GET /api/integrations/status/` shows `ai_tutor` as `live` with the expected `provider`
- [ ] Tutor page → ask a civic question → real reply (not “development response”)
- [ ] Daily usage counter increments (`GET /api/tutor/usage/`)
- [ ] Free-plan limit enforced when quota exceeded

---

## 6. Enterprise SSO — OpenID Connect (optional)

Requires **Enterprise** plan (`sso` feature flag). Configure Entra ID, Okta, or Keycloak as an **OIDC** IdP. SAML assertion consumer (xmlsec) is not in this codebase. Without OIDC settings, status endpoints report `configured: false`.

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

## 6b. Tenant RLS and audit replica (optional, production Postgres)

```env
AUDIT_WORM_PATH=/var/data/backups/audit-worm.jsonl
```

- [ ] Backup cron disk mounted; worm file path is on that disk or object storage with object lock
- [ ] App `DATABASE_URL` uses a **non-superuser** role if you enable RLS
- [ ] Dry-run then apply: `python manage.py enable_tenant_rls --dry-run` then `python manage.py enable_tenant_rls`
- [ ] Confirm seed/migrate still work (empty GUC allows unscoped command access)

Do **not** enable FORCE RLS while Django connects as a Postgres superuser — the owner bypasses policies.

---

## 7. Pre-flight validation

```bash
cd backend
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py check --deploy
```

Expected failures if misconfigured:

| Error | Fix |
|-------|-----|
| `BILLING_PROVIDER must be "stripe"` | For East Africa set `BILLING_PROVIDER=dummy` **and** `ALLOW_DUMMY_BILLING_IN_PRODUCTION=True` |
| `CELERY_BROKER_URL is required` | Set Redis URL |
| Insecure `SECRET_KEY` | Generate new secret |

### Full smoke test (integrations)

- [ ] **Celery**: registration email arrives (worker processing)
- [ ] **Billing**: paid checkout returns 403; Super Admin can assign a plan
- [ ] **SMS**: org broadcast queues and delivers (Pro plan; live AT credentials)
- [ ] **Push**: announcement triggers browser notification
- [ ] **Tutor**: non-stub AI response

Automated HTTP smoke (after deploy):

```bash
cd backend
python manage.py smoke_check --base-url https://api.yourdomain.com --tenant-slug platform-demo
python manage.py check_integrations --strict
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
| `TUTOR_PROVIDER`, `ANTHROPIC_*`, `OPENAI_*` | ✓ | — |
| Email SMTP vars | ✓ | ✓ |

Frontend build (separate static deploy):

| Variable | Required |
|----------|----------|
| `VITE_API_BASE_URL` | Yes |
| `VITE_DEFAULT_TENANT_SLUG` | Yes (usually `platform-demo`) |
| `VITE_VAPID_PUBLIC_KEY` | For push |
| `VITE_SENTRY_DSN` | Recommended |

---

## 9. Disaster recovery

- [ ] Cron/schedule `python manage.py backup_database`
- [ ] Quarterly (or CI): `python manage.py restore_database_drill`
- [ ] Document RPO/RTO with hosting provider — see [disaster-recovery.md](disaster-recovery.md)

---

## 10. Compliance / monitoring gates (production)

Production Django settings also require:

| Variable | Notes |
|----------|--------|
| `EMAIL_HOST` (+ user/password as needed) | Verification and password reset |
| `SENTRY_DSN` | Required when `REQUIRE_SENTRY=True` (default) |
| `REQUIRE_SENTRY=False` | Staging escape hatch only |

After deploy, org admins should download **Organization → Security → Compliance pack** and confirm `integrity.valid` is true. See [compliance-readiness.md](compliance-readiness.md).
