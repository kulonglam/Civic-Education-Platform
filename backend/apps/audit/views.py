from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsModeratorOrAdmin
from apps.tenants.context import get_current_organization

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
        activity_type = self.request.query_params.get('type')
        if activity_type:
            qs = qs.filter(activity_type=activity_type)
        return qs
