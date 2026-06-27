from rest_framework.permissions import BasePermission

from apps.tenants.context import get_current_organization
from apps.tenants.permissions import get_membership


class IsOrgAnalyticsAdmin(BasePermission):
    """Organization owner or admin (analytics plan checked in the view)."""

    message = 'Organization owner or admin role required.'

    def has_permission(self, request, view):
        organization = get_current_organization()
        if organization is None:
            return False
        membership = get_membership(request.user)
        return membership is not None and membership.role in ('owner', 'admin')
