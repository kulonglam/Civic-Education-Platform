# Production credentials — step by step

Do these in order on the **API** service, then copy the same keys to the **Celery worker** where the table says worker=yes. Templates: [backend/.env.production.example](../backend/.env.production.example), [frontend/.env.production.example](../frontend/.env.production.example).

After each optional step, confirm with:

```bash
cd backend
python manage.py check_integrations --json
# or, with a platform-admin JWT:
curl -H "Authorization: Bearer $TOKEN" https://api.yourdomain.com/api/integrations/status/
```

The API process must be **Daphne** (`config.asgi:application`) so `/ws/notifications/` works. Render’s `render.yaml` already starts Daphne. Locally use `start-backend.cmd` or `python -m daphne -b 127.0.0.1 -p 8000 config.asgi:application`.

---

## No custom domain (Render `*.onrender.com`)

You do **not** need to buy a domain. After the first Blueprint deploy, Render assigns two HTTPS URLs. The API will not stay up until `FRONTEND_URL` is that static-site URL (the local-dev default is rejected). Order:

1. Let the Blueprint create both services (the static site URL appears even if the API is crashing).
2. Copy the two URLs from the dashboard (replace the `xxxx` suffix with yours).
3. Set the env vars below, **Manual Deploy** the API, then **Clear build cache & deploy** the static site.

| Service | Example URL |
|---------|-------------|
| API (`civic-education-api`) | `https://civic-education-api-xxxx.onrender.com` |
| Frontend (`civic-education-web`) | `https://civic-education-web-xxxx.onrender.com` |

### API service env (Dashboard → civic-education-api → Environment)

Leave **`ALLOWED_HOSTS` empty** if you want — Render injects `RENDER_EXTERNAL_HOSTNAME` and production settings merge it.

Set these (no trailing slash):

```env
FRONTEND_URL=https://civic-education-web-xxxx.onrender.com
SUPPORT_EMAIL=
REQUIRE_SENTRY=False
```

`FRONTEND_URL` is enough for CORS and WebSockets. You can skip `CORS_ALLOWED_ORIGINS` unless you have extra origins.

`API_BASE_URL` can stay unset on Render; it defaults to this service’s `RENDER_EXTERNAL_URL`.

Email still has to boot: use a free SMTP (Brevo, Resend, or Mailgun) and set `EMAIL_HOST` / user / password / `DEFAULT_FROM_EMAIL`. Production will not start without `EMAIL_HOST`.

The blueprint sets `REQUIRE_SENTRY=False` so you can go live without Sentry. Add `SENTRY_DSN` later and set `REQUIRE_SENTRY=True` when you want boot to fail without it.

Copy `EMAIL_HOST` (and the other SMTP vars) onto the **worker** as well, or verification mail will never send.

### Frontend static site env (then **Clear build cache & deploy**)

```env
VITE_API_BASE_URL=https://civic-education-api-xxxx.onrender.com/api
VITE_DEFAULT_TENANT_SLUG=platform-demo
```

Vite bakes this in at **build** time. Changing it later without a rebuild leaves the SPA talking to the old API URL.

### Your current Render URLs (no custom domain)

| Role | URL |
|------|-----|
| API | `https://civic-education-platform-66rb.onrender.com` |
| Frontend | `https://civic-education-platform-1.onrender.com` |

**API service env** (then Manual Deploy):

```env
FRONTEND_URL=https://civic-education-platform-1.onrender.com
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
REQUIRE_SENTRY=False
```

Leave `ALLOWED_HOSTS` empty. Do not set `FRONTEND_URL` to the API host.

The static site must rewrite unknown paths to `index.html` (already in `render.yaml`). If `/verify-email/...` shows **Not Found**, add that rewrite on the frontend service, or redeploy so `dist/404.html` is published.

**Frontend** build env (then Clear build cache & deploy). Vite needs this at **image/build** time:

```env
VITE_API_BASE_URL=https://civic-education-platform-66rb.onrender.com/api
VITE_DEFAULT_TENANT_SLUG=platform-demo
```

On a Docker frontend, mark `VITE_API_BASE_URL` as available at build time.

### Verification email and SMS (why Gmail never arrived)

Signing up with a Gmail address is not enough. The **API** must send mail through Brevo. Phone OTP is a separate Africa's Talking account. Verification mail sends during the HTTP request (no Celery worker).

**Email — Render free web services block SMTP** (ports 25, 465, 587). That is `[Errno 110] Connection timed out`, not a wrong password. Use Brevo’s **HTTPS API** instead:

1. In Brevo: **SMTP & API → API Keys → Generate a new API key** (this is **not** the SMTP key / `EMAIL_HOST_PASSWORD`).
2. Confirm `makhol1990@gmail.com` (or whichever From address) is a **verified sender**.
3. On the **API** service (`civic-education-platform-66rb`), set:

```env
BREVO_API_KEY=xkeysib-...
DEFAULT_FROM_EMAIL=makhol1990@gmail.com
EMAIL_HOST=smtp-relay.brevo.com
```

`EMAIL_HOST` can stay; production still requires it to boot. Mail will go over HTTPS once `BREVO_API_KEY` is set. Then **Manual Deploy** (this code must be on the API) and click Resend verification.

SMTP on a **paid** Render instance can still use `EMAIL_HOST` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` without the API key.

Then click **Resend verification** on the site. The message should arrive within a minute.

**Phone — not wired until Africa's Talking is set.** Default `SMS_PROVIDER=dummy` only logs OTPs; it never texts a handset. Numbers must be Uganda `+256…`.

```env
SMS_PROVIDER=africastalking
AT_USERNAME=
AT_API_KEY=
AT_SENDER_ID=
```

If the Docker collectstatic fails on `FRONTEND_URL`, you need a dummy in the image build (`https://example.com` is enough for collectstatic). That is already in this repo’s Dockerfiles — redeploy from this commit.

### Free / starter limits

- Web services **sleep** after idle; the first request can take a minute.
- `.github/workflows/keep-awake.yml` pings `/api/ready/` every 10 minutes on GitHub’s schedule (Actions must stay enabled on `main`). That is the keep-alive; the in-app banner only covers a visitor who still hits a cold start.
- Optional repo variables: `KEEP_AWAKE_API_URL`, `KEEP_AWAKE_WEB_URL`.
- `render.yaml` Postgres, Redis, and the worker use **starter** plans. Confirm in the Render dashboard whether those are billed; a sleeping API plus no worker means email/SMS/certificates will queue and never send.
- Keep the worker running if you want bulk SMS, certificate PDFs, and queued jobs. Verification email and phone OTP no longer wait on Celery.

Then continue from Step 1 below for Redis/Celery (already wired in `render.yaml` if those services exist) and optional SMS, WhatsApp, tutor, and push.

---

## Step 1 — Required always: Redis + Celery + SMTP + Sentry + support email

Without these, password reset, verification mail, certificate PDFs, and error tracking will not work in production.

### 1a. Redis (web + worker)

```env
CELERY_BROKER_URL=redis://:password@your-redis-host:6379/0
REDIS_URL=redis://:password@your-redis-host:6379/0
CELERY_TASK_ALWAYS_EAGER=False
```

- [ ] Redis provisioned (Render Redis, ElastiCache, Upstash)
- [ ] Same broker URL on **web** and **worker**
- [ ] Worker running: `celery -A config worker --loglevel=info`
- [ ] `GET https://api.yourdomain.com/api/ready/` returns ready (Postgres + Redis)

### 1b. Email (web + worker)

Render **free** web services block SMTP (ports 25/465/587). Set the Brevo **API** key:

```env
BREVO_API_KEY=
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
EMAIL_HOST=smtp-relay.brevo.com
```

On a paid Render instance you can use SMTP instead (`EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD`).

- [ ] Sender verified in Brevo
- [ ] Send a test: register a user and confirm the verification email arrives
- [ ] `check_integrations` shows `email` as `configured`

### 1c. Sentry (web + worker + frontend build)

```env
SENTRY_DSN=https://your-key@o0.ingest.sentry.io/0
REQUIRE_SENTRY=True
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

Frontend (build-time):

```env
VITE_SENTRY_DSN=https://your-key@o0.ingest.sentry.io/0
VITE_SENTRY_ENVIRONMENT=production
```

- [ ] Create a Sentry project; paste the DSN
- [ ] Trigger a test error and confirm it appears in Sentry

### 1d. Public support email (web)

```env
SUPPORT_EMAIL=support@yourdomain.com
FRONTEND_URL=https://app.yourdomain.com
CORS_ALLOWED_ORIGINS=https://app.yourdomain.com
```

- [ ] `GET /api/branding/` returns that address
- [ ] Contact page shows a mailto link
- [ ] `FRONTEND_URL` matches the SPA origin (required for notification WebSockets)

### 1e. File storage (web + worker)

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_STORAGE_BUCKET=civic-platform
```

- [ ] Create a private bucket; use the **service role** key on the server only
- [ ] Upload an avatar or generate a certificate PDF

East Africa billing stays `BILLING_PROVIDER=dummy` and `ALLOW_DUMMY_BILLING_IN_PRODUCTION=True`. Super Admins assign paid plans in Admin. No Stripe keys required.

---

## Step 2 — SMS (Africa’s Talking) — optional, Pro/Enterprise

Set on **web and worker**.

1. Create an Africa’s Talking account and an app; copy username + API key.
2. Register a sender ID if you will use one (`AT_SENDER_ID`).
3. Set:

```env
SMS_PROVIDER=africastalking
AT_USERNAME=your-at-username
AT_API_KEY=your-at-api-key
AT_SENDER_ID=
```

4. Restart web + worker.
5. As an org owner on a Pro plan, send an SMS alert from Organization.
6. Confirm the phone receives it (worker logs must **not** show `[dummy-sms]`).
7. `check_integrations` → `sms` status `live`.

---

## Step 3 — WhatsApp Cloud API — optional, Pro/Enterprise

Set on **web and worker**. Meta will reject **unsolicited** broadcasts unless you use an **approved template**.

1. In Meta for Developers, create an app → WhatsApp → add a phone number.
2. Copy **permanent** access token and **Phone number ID**.
3. Create a template (example name `civic_alert`) in WhatsApp Manager:
   - Category: Utility or Marketing (as approved)
   - Language: `en` (or `ar`)
   - Body with one variable: `{{1}}` (the platform puts the alert text here)
4. Set a verify token (any long random string) for the webhook handshake.
5. Set:

```env
WHATSAPP_PROVIDER=meta
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_VERIFY_TOKEN=
WHATSAPP_APP_SECRET=
WHATSAPP_DISPLAY_NUMBER=+2567...
WHATSAPP_TEMPLATE_NAME=civic_alert
WHATSAPP_TEMPLATE_LANG=en
WHATSAPP_TEMPLATE_BODY_VARS=1
```

6. Webhook URL: `https://api.yourdomain.com/api/notify/whatsapp/webhook/`  
   Verify token must match `WHATSAPP_VERIFY_TOKEN`. Subscribe to `messages`.
7. Restart web + worker.
8. `GET /api/notify/whatsapp/status/` → `cloud_configured` and `templates_configured` true.
9. Send an org WhatsApp alert on a Pro plan; confirm delivery in WhatsApp Manager.

Without `WHATSAPP_TEMPLATE_NAME`, the API still sends session **text** (only works inside the 24-hour customer-care window).

---

## Step 4 — AI tutor + article translation — optional

Set on the **API web** service (sync request). Same provider fills Arabic article fields on save.

**OpenAI.com is not $0.** This app’s `TUTOR_PROVIDER=openai` talks to any OpenAI-compatible API. On Render, use **Groq’s free tier** (rate-limited, not Claude/GPT).

1. Create a key at [console.groq.com](https://console.groq.com) (no credit card).
2. On the Render **web** service → Environment:

```env
TUTOR_PROVIDER=openai
OPENAI_API_KEY=gsk_...
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=openai/gpt-oss-20b
OPENAI_MAX_TOKENS=1024
ANTHROPIC_API_KEY=
```

Leave `ANTHROPIC_API_KEY` empty. If both are set, `TUTOR_PROVIDER=auto` prefers Anthropic (paid).

3. Save and **restart** the API (or wait for the next deploy).
4. Ask the tutor a civic question. You must **not** see “development response”.
5. `GET /api/integrations/status/` → `ai_tutor` status `live`, `provider` `openai`.

Groq free-tier limits apply per account (requests/minute and per day). If you hit them, the tutor returns unavailable until the window resets.

Paid OpenAI (not free):

```env
TUTOR_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

---

## Step 5 — Web push — optional

Keys must match on backend and frontend **build**.

1. Generate keys:

```bash
npx web-push generate-vapid-keys
```

2. Backend (web + worker):

```env
VAPID_PUBLIC_KEY=BNx...
VAPID_PRIVATE_KEY=...
VAPID_ADMIN_EMAIL=mailto:admin@yourdomain.com
```

3. Frontend **before** `npm run build`:

```env
VITE_VAPID_PUBLIC_KEY=BNx...
```

The public key must match the backend exactly.

4. Rebuild and redeploy the SPA.
5. Log in, allow notifications, trigger an in-app announcement; the browser should show a push.
6. `check_integrations` → `web_push` status `live`.

---

## Step 6 — Enterprise OIDC SSO — optional (Enterprise plan)

1. In Entra ID, Okta, or Keycloak, create an OIDC app.
2. Redirect URI: `https://api.yourdomain.com/api/auth/sso/callback/`
3. Set (web only):

```env
API_BASE_URL=https://api.yourdomain.com
OIDC_ISSUER=https://your-idp.example.com/realms/your-realm
OIDC_CLIENT_ID=
OIDC_CLIENT_SECRET=
OIDC_REDIRECT_URI=https://api.yourdomain.com/api/auth/sso/callback/
OIDC_SCOPES=openid email profile
```

4. In Organization → SSO, enable SSO for that tenant (Enterprise plan).
5. `GET /api/auth/sso/status/?org=your-org-slug` → `configured: true`.
6. Log in with **Sign in with SSO**.

SAML is not implemented; use OIDC.

---

## Step 7 — Final checks

```bash
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py check --deploy
python manage.py check_integrations --strict
python manage.py smoke_check --base-url https://api.yourdomain.com --tenant-slug platform-demo
```

- [ ] Logged-in SPA: notification bell updates without refresh (WebSocket)
- [ ] `CORS_ALLOWED_ORIGINS` includes the exact frontend origin (`https://app.yourdomain.com`, no trailing slash mismatch)

More detail per integration: [production-env-checklist.md](production-env-checklist.md). Deploy topology: [production-launch.md](production-launch.md).
