"""Grade-A enterprise APIs: SCIM tokens, compliance pack, support cases, SLO."""

from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import ActivityLog
from apps.audit.services import log_activity, verify_audit_chain
from apps.billing.models import Subscription
from apps.core.models import SecurityEvent
from apps.core.permissions import IsAdmin
from django.conf import settings
from apps.tenants.context import get_current_organization
from apps.tenants.models import OrganizationScimToken, OrganizationSsoConfig, SupportCase
from apps.tenants.permissions import IsOrgOwnerOrAdmin
from apps.tenants.serializers import SupportCaseSerializer


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


class ScimTokenListCreateView(APIView):
    """Create / list SCIM bearer tokens for the current organization."""

    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]

    def get(self, request):
        organization = get_current_organization()
        tokens = OrganizationScimToken.objects.filter(organization=organization)
        return Response([
            {
                'id': str(t.id),
                'name': t.name,
                'token_prefix': t.token_prefix,
                'is_active': t.is_active,
                'created_at': t.created_at,
                'last_used_at': t.last_used_at,
            }
            for t in tokens
        ])

    def post(self, request):
        organization = get_current_organization()
        name = (request.data.get('name') or 'SCIM token').strip()[:100]
        raw = f'cep_scim_{secrets.token_urlsafe(32)}'
        token = OrganizationScimToken.objects.create(
            organization=organization,
            name=name or 'SCIM token',
            token_prefix=raw[:12],
            token_hash=_hash_token(raw),
        )
        log_activity(
            request.user,
            'admin_action',
            {'action': 'scim_token_created', 'token_id': str(token.id)},
            organization=organization,
            request=request,
        )
        return Response(
            {
                'id': str(token.id),
                'name': token.name,
                'token_prefix': token.token_prefix,
                'token': raw,
                'is_active': token.is_active,
                'created_at': token.created_at,
                'warning': 'Store this token securely. It will not be shown again.',
            },
            status=status.HTTP_201_CREATED,
        )


class ScimTokenRevokeView(APIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]

    def delete(self, request, token_id):
        organization = get_current_organization()
        token = get_object_or_404(OrganizationScimToken, pk=token_id, organization=organization)
        token.is_active = False
        token.save(update_fields=['is_active'])
        log_activity(
            request.user,
            'admin_action',
            {'action': 'scim_token_revoked', 'token_id': str(token.id)},
            organization=organization,
            request=request,
        )
        return Response({'message': 'SCIM token revoked.'})


class ComplianceEvidencePackView(APIView):
    """Download a compliance evidence pack for audits (ISO/SOC-style evidence)."""

    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]

    def get(self, request):
        organization = get_current_organization()
        sso = OrganizationSsoConfig.objects.filter(organization=organization).first()
        sub = (
            Subscription.objects.filter(organization=organization)
            .select_related('plan')
            .first()
        )
        chain = verify_audit_chain(organization=organization, limit=200)
        recent = list(
            ActivityLog.objects.filter(organization=organization)
            .order_by('-timestamp')[:20]
            .values(
                'id',
                'activity_type',
                'timestamp',
                'integrity_hash',
                'prev_hash',
                'ip_address',
            )
        )
        scim_active = OrganizationScimToken.objects.filter(
            organization=organization, is_active=True
        ).count()
        pack = {
            'generated_at': timezone.now().isoformat(),
            'pack_version': 2,
            'framework_note': (
                'Evidence for SOC 2 / ISO 27001 readiness reviews. '
                'This pack documents product controls; it is not a certification.'
            ),
            'organization': {
                'id': str(organization.id),
                'name': organization.name,
                'slug': organization.slug,
                'force_mfa_for_admins': organization.force_mfa_for_admins,
                'audit_retention_days': organization.audit_retention_days,
                'ip_allowlist_configured': bool(organization.ip_allowlist),
                'ip_allowlist_count': len(organization.ip_allowlist or []),
            },
            'controls': {
                'sso_enabled': bool(sso and sso.enabled),
                'sso_ready': bool(sso and sso.is_ready),
                'mfa_enforced_for_admins': organization.force_mfa_for_admins,
                'audit_hash_chain_valid': chain['valid'],
                'audit_hash_chain_checked': chain['checked'],
                'session_idle_timeout_seconds': int(settings.SESSION_IDLE_TIMEOUT_SECONDS),
                'jwt_cookies_httponly': True,
                'scim_active_tokens': scim_active,
                'plan_code': sub.plan.code if sub and sub.plan_id else None,
            },
            'control_matrix': [
                {
                    'id': 'AC-1',
                    'theme': 'Access control',
                    'soc2': 'CC6.1',
                    'iso27001': 'A.5.15 / A.8.2',
                    'status': 'implemented',
                    'evidence': 'Org RBAC roles; force_mfa_for_admins; SSO/OIDC optional',
                },
                {
                    'id': 'AC-2',
                    'theme': 'Identity lifecycle',
                    'soc2': 'CC6.2',
                    'iso27001': 'A.5.16',
                    'status': 'implemented',
                    'evidence': 'SCIM 2.0 Users/Groups; invite + bulk import; membership revoke',
                },
                {
                    'id': 'AU-1',
                    'theme': 'Audit logging',
                    'soc2': 'CC7.2',
                    'iso27001': 'A.8.15',
                    'status': 'implemented',
                    'evidence': 'ActivityLog with integrity hash chain; export CSV/JSON',
                },
                {
                    'id': 'AU-2',
                    'theme': 'Session security',
                    'soc2': 'CC6.6',
                    'iso27001': 'A.8.5',
                    'status': 'implemented',
                    'evidence': 'Server idle timeout; session_epoch revocation; httpOnly JWT cookies',
                },
                {
                    'id': 'NS-1',
                    'theme': 'Network restriction',
                    'soc2': 'CC6.6',
                    'iso27001': 'A.8.20',
                    'status': 'implemented' if organization.ip_allowlist else 'available',
                    'evidence': 'Per-tenant IP allowlist middleware',
                },
                {
                    'id': 'PR-1',
                    'theme': 'Privacy / DSAR',
                    'soc2': 'P4.2 / P5.1',
                    'iso27001': 'A.8.10',
                    'status': 'implemented',
                    'evidence': '/api/users/me/export/ and /api/users/me/deactivate/',
                },
                {
                    'id': 'CM-1',
                    'theme': 'Change & content governance',
                    'soc2': 'CC8.1',
                    'iso27001': 'A.8.32',
                    'status': 'implemented',
                    'evidence': 'Article approval workflow; controlled documents; locked categories',
                },
            ],
            'evidence': {
                'recent_audit_sample': recent,
                'endpoints': {
                    'audit_export': '/api/audit/logs/export/',
                    'compliance_verify': '/api/organization/compliance/verify/',
                    'scim_users': '/scim/v2/Users',
                    'scim_groups': '/scim/v2/Groups',
                    'slo': '/api/organization/platform/slo/',
                    'dsar_export': '/api/users/me/export/',
                    'dsar_deactivate': '/api/users/me/deactivate/',
                },
                'policy_checklist': [
                    'Access control: org RBAC + MFA for admins',
                    'Audit logging with integrity hash chain',
                    'Session idle timeout + JWT session epoch revocation',
                    'Optional IP allowlist for tenant traffic',
                    'SCIM 2.0 user provisioning for IdP sync',
                    'Data export and account deactivation (DSAR)',
                    'TLS, HSTS, CSP, and secure cookie flags in production',
                    'Dependency vulnerability monitoring (pip-audit / npm audit)',
                ],
            },
            'integrity': chain,
        }
        log_activity(
            request.user,
            'compliance_pack_exported',
            {'checked': chain['checked'], 'valid': chain['valid']},
            organization=organization,
            request=request,
        )
        return Response(pack)


class AuditIntegrityVerifyView(APIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]

    def get(self, request):
        organization = get_current_organization()
        return Response(verify_audit_chain(organization=organization, limit=1000))


class SupportCaseListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]

    def get(self, request):
        organization = get_current_organization()
        cases = SupportCase.objects.filter(organization=organization)
        return Response(SupportCaseSerializer(cases, many=True).data)

    def post(self, request):
        organization = get_current_organization()
        serializer = SupportCaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        case = serializer.save(organization=organization, created_by=request.user)
        log_activity(
            request.user,
            'support_case_opened',
            {'case_id': str(case.id), 'subject': case.subject},
            organization=organization,
            request=request,
        )
        return Response(SupportCaseSerializer(case).data, status=status.HTTP_201_CREATED)


class SupportCaseDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]

    def patch(self, request, case_id):
        organization = get_current_organization()
        case = get_object_or_404(SupportCase, pk=case_id, organization=organization)
        # Tenants may only close their own cases (not rewrite assignee notes).
        status_value = request.data.get('status')
        if status_value in (SupportCase.STATUS_CLOSED, SupportCase.STATUS_RESOLVED):
            case.status = status_value
            case.save(update_fields=['status', 'updated_at'])
            log_activity(
                request.user,
                'support_case_updated',
                {'case_id': str(case.id), 'status': case.status},
                organization=organization,
                request=request,
            )
        return Response(SupportCaseSerializer(case).data)


class PlatformSupportCaseListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        status_filter = request.query_params.get('status')
        qs = SupportCase.objects.select_related('organization', 'created_by').all()
        if status_filter:
            qs = qs.filter(status=status_filter)
        return Response(SupportCaseSerializer(qs[:100], many=True).data)


class PlatformSupportCaseUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, case_id):
        case = get_object_or_404(SupportCase, pk=case_id)
        serializer = SupportCaseSerializer(case, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_activity(
            request.user,
            'support_case_updated',
            {'case_id': str(case.id), 'status': case.status, 'platform': True},
            organization=case.organization,
            request=request,
        )
        return Response(SupportCaseSerializer(case).data)


class SloMetricsView(APIView):
    """Service-level objective snapshot for ops / enterprise reporting."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        now = timezone.now()
        window = now - timedelta(hours=24)
        events = SecurityEvent.objects.filter(created_at__gte=window)
        totals = events.values('event_type').annotate(c=Count('id'))
        by_type = {row['event_type']: row['c'] for row in totals}
        login_ok = by_type.get('login_success', 0)
        login_fail = by_type.get('login_failed', 0) + by_type.get('mfa_verify_failed', 0)
        login_total = login_ok + login_fail
        login_success_rate = (login_ok / login_total) if login_total else 1.0
        permission_denied = by_type.get('permission_denied', 0)
        open_cases = SupportCase.objects.filter(
            status__in=(SupportCase.STATUS_OPEN, SupportCase.STATUS_IN_PROGRESS)
        ).count()

        availability_target = 99.9
        # Proxy: treat high auth failure or permission spikes as degraded.
        status_label = 'healthy'
        if login_total >= 20 and login_success_rate < 0.9:
            status_label = 'degraded'
        if permission_denied > 100:
            status_label = 'degraded'

        return Response({
            'generated_at': now.isoformat(),
            'window_hours': 24,
            'targets': {
                'availability_percent': availability_target,
                'auth_success_rate_percent': 99.0,
            },
            'observed': {
                'auth_success_rate_percent': round(login_success_rate * 100, 3),
                'login_success_24h': login_ok,
                'login_failure_24h': login_fail,
                'security_events_24h': events.count(),
                'permission_denied_24h': permission_denied,
                'open_support_cases': open_cases,
                'events_by_type': by_type,
            },
            'status': status_label,
            'probes': {
                'health': '/api/health/',
                'ready': '/api/ready/',
                'security_events': '/api/security/events/',
            },
            'notes': (
                'Auth/security metrics are derived from SecurityEvent rows. '
                'Pair with Sentry + external uptime probes (/api/health/, /api/ready/) '
                'for contractual SLO reporting.'
            ),
        })
