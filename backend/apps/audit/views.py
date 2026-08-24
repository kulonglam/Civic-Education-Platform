import csv
import io
from datetime import timedelta

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import log_activity
from apps.accounts.roles import is_platform_admin
from apps.core.permissions import IsModeratorOrAdmin
from apps.tenants.context import get_current_organization
from apps.tenants.permissions import IsOrgOwnerOrAdmin

from .models import ActivityLog
from .serializers import ActivityLogSerializer


class ActivityLogListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsModeratorOrAdmin]
    serializer_class = ActivityLogSerializer

    def get_queryset(self):
        qs = ActivityLog.objects.select_related('user', 'organization').all()
        organization = get_current_organization()
        if organization is not None:
            qs = qs.filter(organization=organization)
        elif not is_platform_admin(self.request.user):
            # Fail closed: org/moderator operators never see another tenant's
            # logs just because no X-Tenant-Slug was sent.
            qs = qs.none()
        activity_type = self.request.query_params.get('type')
        if activity_type:
            qs = qs.filter(activity_type=activity_type)
        date_from = self.request.query_params.get('from')
        date_to = self.request.query_params.get('to')
        if date_from:
            qs = qs.filter(timestamp__date__gte=date_from)
        if date_to:
            qs = qs.filter(timestamp__date__lte=date_to)
        return qs


class ActivityLogExportView(APIView):
    """Export org activity logs as CSV or JSON for compliance reviews."""

    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]

    def get(self, request):
        organization = get_current_organization()
        qs = ActivityLog.objects.filter(organization=organization).select_related('user').order_by('-timestamp')
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')
        if date_from:
            qs = qs.filter(timestamp__date__gte=date_from)
        if date_to:
            qs = qs.filter(timestamp__date__lte=date_to)
        fmt = (request.query_params.get('format') or 'csv').lower()
        qs = qs[:5000]

        log_activity(
            request.user,
            'data_exported',
            {'resource': 'audit_logs', 'format': fmt, 'count': qs.count()},
            organization=organization,
            request=request,
        )

        if fmt == 'json':
            data = ActivityLogSerializer(qs, many=True).data
            return Response({'results': data, 'count': len(data)})

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(['timestamp', 'activity_type', 'user_email', 'ip_address', 'user_agent', 'metadata'])
        for row in qs:
            writer.writerow([
                row.timestamp.isoformat(),
                row.activity_type,
                row.user.email if row.user_id else '',
                row.ip_address or '',
                row.user_agent,
                row.metadata,
            ])
        response = HttpResponse(buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="audit-export.csv"'
        return response
