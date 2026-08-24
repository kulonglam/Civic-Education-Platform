import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsSuperAdmin

from .models import SecurityEvent
from .serializers import HealthSerializer

from .integrations import (
    STATUS_DEGRADED,
    STATUS_EAGER,
    STATUS_LIVE,
    build_integrations_report,
    check_cache,
    check_celery,
    check_database,
)

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """Liveness probe: confirms the process is up and serving."""

    permission_classes = [AllowAny]
    serializer_class = HealthSerializer

    @extend_schema(responses=HealthSerializer)
    def get(self, request):
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class ReadinessCheckView(APIView):
    """Readiness probe: verifies dependencies (database, cache) are reachable."""

    permission_classes = [AllowAny]
    serializer_class = HealthSerializer

    @extend_schema(responses=HealthSerializer)
    def get(self, request):
        db = check_database()
        cache = check_cache()
        celery = check_celery()

        checks = {
            'database': db['status'],
            'cache': cache['status'],
            'celery': celery['status'],
        }

        from django.conf import settings as dj_settings

        checks['sentry_configured'] = 'ok' if getattr(dj_settings, 'SENTRY_DSN', '') else 'unset'

        core_ok = db['status'] == STATUS_LIVE and cache['status'] == STATUS_LIVE
        celery_ok = celery['status'] in (STATUS_LIVE, STATUS_EAGER)
        healthy = core_ok and celery_ok

        payload = {
            'status': 'ready' if healthy else 'degraded',
            **checks,
            'database_detail': db.get('detail', ''),
            'cache_detail': cache.get('detail', ''),
            'celery_detail': celery.get('detail', ''),
            'observability': {
                'sentry': checks['sentry_configured'],
                'health': '/api/health/',
                'ready': '/api/ready/',
                'integrations': '/api/integrations/status/',
                'slo': '/api/organization/platform/slo/',
                'security_events': '/api/security/events/',
            },
        }
        if celery.get('meta'):
            payload['celery_workers'] = celery['meta'].get('workers', [])

        return Response(
            payload,
            status=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class IntegrationsStatusView(APIView):
    """Platform admin: full integration status (Stripe, Celery, SMS, tutor, etc.)."""

    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(responses=dict)
    def get(self, request):
        report = build_integrations_report(include_infra=True)
        return Response(report, status=status.HTTP_200_OK)


class SecurityEventListView(APIView):
    """Platform admin: recent security events (failed logins, MFA, etc.)."""

    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        qs = SecurityEvent.objects.all()
        event_type = (request.query_params.get('event_type') or '').strip()
        if event_type:
            qs = qs.filter(event_type=event_type)
        try:
            limit = min(int(request.query_params.get('page_size') or 50), 200)
        except (TypeError, ValueError):
            limit = 50
        rows = []
        for event in qs[:limit]:
            rows.append({
                'id': str(event.id),
                'event_type': event.event_type,
                'user_id': str(event.user_id) if event.user_id else None,
                'user_email': event.user_email,
                'ip_address': event.ip_address,
                'path': event.path,
                'method': event.method,
                'detail': event.detail,
                'created_at': event.created_at,
            })
        return Response({'results': rows, 'count': len(rows)})
