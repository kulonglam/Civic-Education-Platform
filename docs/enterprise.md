# Enterprise features (Government / NGO)

Institutional capabilities for ministries, counties, and NGO training partners.

## Security & compliance

| Feature | Where |
|---------|--------|
| Per-organization OIDC SSO | Organization → SSO (Enterprise plan); API `/api/organization/sso/` |
| Fail-closed tenant queries | API requests without a resolved org return empty tenant querysets (not all tenants) |
| Optional Postgres RLS | `python manage.py enable_tenant_rls` on a **non-superuser** app role (opt-in; not a default migration) |
| Audit export (CSV/JSON) | Organization settings → Export audit; `/api/audit/logs/export/` |
| Audit integrity hash chain | Auto on every `log_activity`; verify `/api/organization/compliance/verify/` |
| Append-only activity logs | `ActivityLog.save` rejects updates except the create-then-hash write |
| Off-box audit replica | Set `AUDIT_WORM_PATH` (JSONL append). Use the backup disk or object lock storage |
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
| Government IdP | Use Entra ID, Okta, or Keycloak **OIDC**. SAML ACS / xmlsec is not implemented |

## Org structure & scale

| Feature | Where |
|---------|--------|
| Departments | Organization → Departments; memberships/invites accept `department_id` |
| Roles | `owner`, `admin`, `content_manager`, `moderator`, `member` |
| Org RBAC | `content_manager` → articles/quizzes; `moderator` → forum moderation |
| CSV bulk invite | Organization → Bulk import (`dry_run` supported) |
| Platform tenant console | Admin → Organizations (activate/deactivate, assign plan) |
| Invoice / card-upgrade plans | Super Admin → Organizations → plan dropdown; `POST /api/organization/platform/orgs/<id>/plan/` |
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
| Off-site backup copy | `backup_database` uploads to configured storage under `backups/` when credentials exist |
| Locust CI gate | `.github/workflows/ci.yml` job `loadtest` — gunicorn, 20 users / 30s, fail ratio + p95 |

## Billing (East Africa)

Stripe Checkout is **not** the production path (Stripe is unavailable as a merchant in Uganda / South Sudan). Production uses `BILLING_PROVIDER=dummy` with `ALLOW_DUMMY_BILLING_IN_PRODUCTION=True`. Paid self-serve checkout returns **403**; Super Admins assign Pro/Enterprise after invoice or card upgrade. Org admins cannot assign plans or upgrade via `/api/billing/checkout/` for paid codes.

## Grade-A controls (summary)

Enterprise buyers get **server-enforced** session idle timeout and JWT revocation, **SCIM** for IdP lifecycle, **tamper-evident audit hashes** plus an optional JSONL replica, a downloadable **compliance evidence pack**, **IP allowlisting**, **support cases**, and an **SLO metrics** API for ops reporting. Tenant lists fail closed on the API when no organization is resolved.

## Certification readiness

Product controls map to SOC 2 / ISO 27001 themes in [compliance-readiness.md](compliance-readiness.md). Use the in-app compliance pack plus that checklist for buyer diligence; formal certification still requires an external auditor and operating policies.

## What this repo cannot certify as 10/10

A true enterprise **10/10** needs operator evidence that does not live in application code:

- Independent pentest with a closed finding list
- SOC 2 Type II or ISO 27001
- Measured 99.9% SLO history and a staffed support SLA
- Timed PITR restore on the real host; multi-region failover
- Locust/k6 evidence at the SRS concurrent-user target (CI is a smoke gate, not 10k users)
- Live Africa’s Talking / Meta WhatsApp credentials (dummy until env is set)
- `enable_tenant_rls` on a **non-superuser** database role (FORCE RLS on the table owner that is superuser is a no-op)
