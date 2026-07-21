# Enterprise features (Government / NGO)

Institutional capabilities for ministries, counties, and NGO training partners.

## Security & compliance

| Feature | Where |
|---------|--------|
| Per-organization OIDC SSO | Organization → SSO (Enterprise plan); API `/api/organization/sso/` |
| Audit export (CSV/JSON) | Organization settings → Export audit; `/api/audit/logs/export/` |
| Audit integrity hash chain | Auto on every `log_activity`; verify `/api/organization/compliance/verify/` |
| Compliance evidence pack | Organization → Download compliance pack; `/api/organization/compliance/pack/` |
| Audit retention purge | `python manage.py purge_audit_logs` (weekly Render cron) |
| Download my data / deactivate | Profile page; `/api/users/me/export/`, `/api/users/me/deactivate/` |
| Force MFA for org admins | Organization branding/settings |
| Server-side idle timeout | Privileged roles; `SESSION_IDLE_TIMEOUT_SECONDS` (default 30 min) |
| Session revocation (epoch) | Password change / deactivate / suspend / logout `revoke_all` bumps `session_epoch` |
| IP allowlist | Organization settings; empty = allow all |
| Security event dashboard | Admin → Security events; API `/api/security/events/` |

## Identity provisioning

| Feature | Where |
|---------|--------|
| SCIM 2.0 Users + Groups | `POST/GET/PATCH/DELETE /scim/v2/Users` and `/scim/v2/Groups` (Groups map to departments) |
| SCIM token management | Organization → Security → SCIM; `/api/organization/scim/tokens/` |
| Cookie-first JWT sessions | httpOnly cookies + in-memory access; refresh via cookie at `/api/auth/token/refresh/` |

## Org structure & scale

| Feature | Where |
|---------|--------|
| Departments | Organization → Departments; memberships/invites accept `department_id` |
| Roles | `owner`, `admin`, `content_manager`, `moderator`, `member` |
| Org RBAC | `content_manager` → articles/quizzes; `moderator` → forum moderation |
| CSV bulk invite | Organization → Bulk import (`dry_run` supported) |
| Platform tenant console | Admin → Organizations (activate/deactivate) |
| View org as support | Admin → Organizations → View as support (read-only metrics) |
| Cross-org usage | Admin → Cross-organization usage; API `/api/organization/platform/usage/` |
| Support cases | Organization → Enterprise support; platform `/api/organization/platform/support/cases/` |
| SLO snapshot | Platform admin `/api/organization/platform/slo/` |

## Content governance & reporting

| Feature | Where |
|---------|--------|
| Article approval | Editors/content managers publish → `pending_review`; org/platform admins approve |
| Locked curriculum categories | Categories → lock as official curriculum (`is_locked`) |
| Controlled documents | Article editor → controlled document + label + version |
| Institutional PDF report | Dashboard → Download PDF report |

## Production ops

| Feature | Where |
|---------|--------|
| Read replica | Set `DATABASE_URL_REPLICA` — router in `apps.core.db.ReadReplicaRouter` |
| Render / Sentry / backups | See [production-launch.md](production-launch.md) and [scaling.md](scaling.md) |
| Disaster recovery drill | `python manage.py restore_database_drill` — [disaster-recovery.md](disaster-recovery.md) |
| Locust CI gate | `.github/workflows/ci.yml` job `loadtest` — fail ratio + p95 thresholds |

## Grade-A controls (summary)

Enterprise buyers get **server-enforced** session idle timeout and JWT revocation, **SCIM** for IdP lifecycle, **tamper-evident audit hashes**, a downloadable **compliance evidence pack**, **IP allowlisting**, **support cases**, and an **SLO metrics** API for ops reporting.

## Certification readiness

Product controls map to SOC 2 / ISO 27001 themes in [compliance-readiness.md](compliance-readiness.md). Use the in-app compliance pack plus that checklist for buyer diligence; formal certification still requires an external auditor and operating policies.
