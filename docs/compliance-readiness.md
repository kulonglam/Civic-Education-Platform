# Compliance readiness (SOC 2 / ISO 27001)

This document maps **product controls that already ship** to common audit themes. It supports enterprise buyer reviews and certification prep.

**Important:** downloading a compliance pack or completing this checklist is **not** an SOC 2 or ISO certificate. Formal certification requires an independent auditor, policies, and operating evidence (logs, tickets, change records) outside the application.

See also: [enterprise.md](enterprise.md), [production-launch.md](production-launch.md), [production-env-checklist.md](production-env-checklist.md), [disaster-recovery.md](disaster-recovery.md).

---

## Control matrix

| ID | Theme | SOC 2 | ISO 27001 | Product evidence |
|----|--------|-------|-----------|------------------|
| AC-1 | Access control | CC6.1 | A.5.15 / A.8.2 | Org RBAC; `force_mfa_for_admins`; OIDC SSO |
| AC-2 | Identity lifecycle | CC6.2 | A.5.16 | SCIM Users/Groups; invites; bulk CSV import |
| AU-1 | Audit logging | CC7.2 | A.8.15 | Hash-chained `ActivityLog`; CSV/JSON export; verify API |
| AU-2 | Session security | CC6.6 | A.8.5 | Idle timeout; `session_epoch` revoke; httpOnly JWT cookies |
| NS-1 | Network restriction | CC6.6 | A.8.20 | Per-tenant IP allowlist |
| PR-1 | Privacy / DSAR | P4–P5 | A.8.10 | `/api/users/me/export/`, deactivate |
| CM-1 | Content governance | CC8.1 | A.8.32 | Article approval; controlled docs; locked categories |
| OP-1 | Monitoring | CC7.1 | A.8.16 | Sentry (required in prod); SLO API; security events |
| OP-2 | Secure SDLC | CC8.1 | A.8.25 | `pip-audit` / `npm audit`; CI tests; production fail-fast |

---

## Evidence pack (in-product)

Organization owners/admins can download:

`GET /api/organization/compliance/pack/`

Includes organization control flags, audit chain integrity result, recent audit sample, control matrix, and endpoint inventory.

Verify chain only:

`GET /api/organization/compliance/verify/`

---

## Production security baseline (must be true before audit)

- [ ] `DJANGO_SETTINGS_MODULE=config.settings.production`
- [ ] `SECRET_KEY` strong; `BILLING_PROVIDER=stripe`
- [ ] Redis + Celery worker live; `/api/ready/` green
- [ ] `EMAIL_HOST` configured (verification / reset)
- [ ] `SENTRY_DSN` set (`REQUIRE_SENTRY=True` by default)
- [ ] HTTPS + HSTS; JWT cookies Secure + httpOnly
- [ ] Weekly `purge_audit_logs` cron
- [ ] Backups + restore drill documented
- [ ] Dependency audits clean: `pip-audit -r requirements.txt`, `npm audit`

---

## Recurring ops (auditor will ask)

| Cadence | Activity |
|---------|----------|
| Weekly | Review security events / failed logins |
| Weekly | `pip-audit` / `npm audit` in CI or release checklist |
| Monthly | Sample audit export + chain verify for a pilot org |
| Quarterly | Access review (org owners, SCIM tokens, platform admins) |
| On hire/exit | Disable memberships; rotate SCIM / SSO secrets |

---

## What certification still requires (outside this repo)

1. Written information security policy, access policy, incident response plan  
2. Vendor risk / DPA with hosting (Render, Supabase, Stripe, etc.)  
3. Penetration test or vulnerability assessment report  
4. Evidence of ticketed change management for production deploys  
5. Engagement with a licensed SOC 2 / ISO auditor  

The platform is built so those reviews can **point at real controls**, not slideware.
