from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.tenants.models import Membership
from apps.tenants.permissions import (
    CanDeleteOrgContent,
    IsOrgContentEditor,
    IsOrgMember,
    get_membership,
)

from .models import CivicNews
from .serializers import CivicNewsSerializer


def _can_see_unpublished(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    role = getattr(user, 'role', None)
    if role and role.name in ('editor', 'admin', 'super_admin', 'moderator'):
        return True
    membership = get_membership(user)
    return membership is not None and membership.role in (
        Membership.OWNER,
        Membership.ADMIN,
        Membership.CONTENT_MANAGER,
        Membership.MODERATOR,
    )


class CivicNewsFilter(filters.FilterSet):
    topic = filters.CharFilter()
    claim_type = filters.CharFilter()
    status = filters.CharFilter()

    class Meta:
        model = CivicNews
        fields = ['topic', 'claim_type', 'status']


class CivicNewsViewSet(viewsets.ModelViewSet):
    serializer_class = CivicNewsSerializer
    filterset_class = CivicNewsFilter
    search_fields = ['title', 'title_ar', 'body', 'body_ar', 'source_name']
    ordering_fields = ['published_at', 'created_at', 'title']
    lookup_field = 'id'

    def get_queryset(self):
        qs = CivicNews.objects.select_related('created_by').all()
        if not _can_see_unpublished(self.request.user):
            qs = qs.filter(status=CivicNews.STATUS_PUBLISHED)
        return qs

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsOrgMember(), CanDeleteOrgContent()]
        return [IsAuthenticated(), IsOrgMember(), IsOrgContentEditor()]

    def perform_create(self, serializer):
        extras = {'created_by': self.request.user}
        if serializer.validated_data.get('status') == CivicNews.STATUS_PUBLISHED:
            extras.setdefault('published_at', timezone.now())
        serializer.save(**extras)

    def perform_update(self, serializer):
        instance = self.get_object()
        extras = {}
        new_status = serializer.validated_data.get('status', instance.status)
        if new_status == CivicNews.STATUS_PUBLISHED and not instance.published_at:
            extras['published_at'] = timezone.now()
        serializer.save(**extras)
