# Civic Education RSS API Reference

Base URL: `/api/`

**Authoritative API docs:** run the backend and open [`/api/docs/`](http://127.0.0.1:8000/api/docs/) (Swagger UI generated from code). This file is a quick index — it may lag behind the live schema.

## Conventions

- **Tenant header:** `X-Organization-Slug: your-org-slug` (citizens default to `platform-demo` after `seed_data`)
- **Auth:** `Authorization: Bearer <access_token>`
- **Roles:** Platform roles (`citizen`, `moderator`, `editor`, `admin`) are separate from org membership (`owner`, `admin`, `member`). Org signup creates platform `editor` + org `owner`.

## Endpoint index

| Area | Prefix | Notes |
|------|--------|-------|
| Auth | `/auth/` | Register, login, JWT refresh, email/phone verify, password reset, **Enterprise SSO (OIDC)** |
| Users | `/users/` | Profile, avatar, suspend/unsuspend, platform role (admin only), data export |
| Organization | `/organization/` | Current org, members, invites, departments, leave |
| Billing | `/billing/` | Plans, Stripe checkout/portal/webhook |
| Articles | `/articles/` | CRUD; public list when published; attachments, controlled docs, progress |
| Categories | `/categories/` | Org-scoped taxonomy (Constitution, Governance, Elections, Peacebuilding) |
| Media | `/media/` | Audio/video library; uploads + external URLs; captions URL; public when published |
| Quizzes | `/quizzes/` | CRUD, attempts, results, certificates |
| Forum | `/topics/`, `/comments/` | Topics, comments, moderation |
| Notifications | `/notifications/` | In-app list, read, org broadcast, web push subscribe, **push stats/cleanup (platform admin)** |
| SMS | `/notify/` | Org/platform SMS (Pro+ plan) |
| Tutor | `/tutor/` | RAG-grounded AI chat, SSE streaming, session, history, usage — see [tutor-rag.md](tutor-rag.md) |
| Gamification | `/gamification/` | XP, level, badges (`GET /gamification/me/`) |
| Engagement | `/engagement/` | Polls, petitions, campaigns (vote/sign) |
| Search | `/search/` | Unified search across articles, media, forum topics |
| Analytics | `/analytics/` | Platform admin overview; org dashboard (Pro+); personal `GET /analytics/me/` |
| Audit | `/audit/logs/` | Org-scoped activity log (moderator+) |
| Content bundle | `/content-bundle/` | Offline study pack manifest + download |
| System | `/health/`, `/ready/`, `/integrations/status/` | Liveness, DB/Redis/Celery readiness, full integration report (platform admin) |

## Tutor API (summary)

Full detail: [tutor-rag.md](tutor-rag.md) · Constitution workflow: [constitution-content.md](constitution-content.md)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/tutor/chat/` | User + org | JSON chat; returns `reply` + `sources[]` |
| POST | `/tutor/chat/stream/` | User + org | SSE stream (`token`, `done`, `error` events) |
| GET | `/tutor/chat/session/` | User + org | Restore active session (~1 h Redis TTL) |
| DELETE | `/tutor/chat/session/` | User + org | Clear active session |
| GET | `/tutor/chat/history/` | User + org | List saved conversation summaries |
| GET | `/tutor/chat/history/<session_id>/` | User + org | Load one conversation |
| GET | `/tutor/usage/` | User + org | Daily message quota for current user |
| GET | `/tutor/usage/platform/` | **Platform admin** | Today's messages, tokens, active users |

Optional request field on chat endpoints: `article_id` (UUID) — boosts retrieval from that article.

## Gamification & engagement

| Method | Path | Description |
|--------|------|-------------|
| GET | `/gamification/me/` | Level, XP, badges earned |
| GET | `/engagement/polls/` | List open/closed polls |
| POST | `/engagement/polls/` | Create poll (content editor+) |
| POST | `/engagement/polls/<id>/vote/` | Cast vote (awards XP) |
| GET | `/engagement/petitions/` | List petitions |
| POST | `/engagement/petitions/` | Create petition (content editor+) |
| POST | `/engagement/petitions/<id>/sign/` | Sign petition (awards XP) |
| GET | `/engagement/campaigns/` | List campaigns |
| POST | `/engagement/campaigns/` | Create campaign (content editor+) |

## Related docs

- [tutor-rag.md](tutor-rag.md) — AI tutor retrieval, PDF grounding, streaming, admin usage
- [constitution-content.md](constitution-content.md) — seed + editor workflow for constitution PDFs
- [testing.md](testing.md) — pytest, Vitest, Playwright e2e (mocked + live)
- [production-launch.md](production-launch.md)
- [production-env-checklist.md](production-env-checklist.md)
- [scaling.md](scaling.md)

## Ops commands

```bash
cd backend
python manage.py seed_data              # roles, plans, demo org + sample content
python manage.py check_integrations     # Stripe, Celery, SMS, Anthropic, VAPID, etc.
python manage.py check_integrations --json
python manage.py check_integrations --strict   # exit 1 if required integrations missing
python manage.py demote_legacy_org_admins --dry-run
python manage.py backfill_audit_orgs --dry-run
python manage.py smoke_check --base-url https://api.yourdomain.com
```

Regenerate PWA icons after brand changes:

```bash
python scripts/generate_pwa_icons.py
```
