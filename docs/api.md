# Civic Education Platform API Reference

Base URL: `/api/`

**Authoritative API docs:** run the backend and open [`/api/docs/`](http://127.0.0.1:8000/api/docs/) (Swagger UI generated from code). This file is a quick index only — it may lag behind the live schema.

## Conventions

- **Tenant header:** `X-Organization-Slug: your-org-slug` (citizens default to `platform-demo` after `seed_data`)
- **Auth:** `Authorization: Bearer <access_token>`
- **Roles:** Platform roles (`citizen`, `moderator`, `editor`, `admin`) are separate from org membership (`owner`, `admin`, `member`). Org signup creates platform `editor` + org `owner`.

## Endpoint index

| Area | Prefix | Notes |
|------|--------|-------|
| Auth | `/auth/` | Register, login, JWT refresh, email/phone verify, password reset, **Enterprise SSO (OIDC)** |
| Users | `/users/` | Profile, avatar, suspend/unsuspend, platform role (admin only) |
| Organization | `/organization/` | Current org, members, invites, leave |
| Billing | `/billing/` | Plans, Stripe checkout/portal/webhook |
| Articles | `/articles/` | CRUD; public list when published |
| Categories | `/categories/` | Org-scoped taxonomy |
| Quizzes | `/quizzes/` | CRUD, attempts, results, certificates |
| Forum | `/topics/`, `/comments/` | Topics, comments, moderation |
| Notifications | `/notifications/` | In-app list, read, org broadcast, web push subscribe, **push stats/cleanup (platform admin)** |
| SMS | `/notify/` | Org/platform SMS (Pro+ plan) |
| Tutor | `/tutor/` | AI chat + usage |
| Analytics | `/analytics/` | Platform admin overview; org dashboard (Pro+ plan) |
| Audit | `/audit/logs/` | Org-scoped activity log (moderator+) |
| System | `/health/`, `/ready/` | Liveness + DB/Redis readiness |

## Related docs

- [production-launch.md](production-launch.md)
- [production-env-checklist.md](production-env-checklist.md)
- [scaling.md](scaling.md)

## Ops commands

```bash
cd backend
python manage.py seed_data              # roles, plans, demo org + sample content
python manage.py demote_legacy_org_admins --dry-run
python manage.py backfill_audit_orgs --dry-run
python manage.py smoke_check --base-url https://api.yourdomain.com
```

Regenerate PWA icons after brand changes:

```bash
python scripts/generate_pwa_icons.py
```
