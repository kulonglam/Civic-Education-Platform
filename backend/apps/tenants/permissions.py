from rest_framework.permissions import BasePermission

from apps.accounts.permissions import check_mfa_enrolled

from .context import get_current_organization
from .models import Membership


def get_membership(user):
    organization = get_current_organization()
    if organization is None or not user or not user.is_authenticated:
        return None
    return Membership.objects.filter(organization=organization, user=user).first()


class IsOrgMember(BasePermission):
    message = 'You are not a member of this organization.'

    def has_permission(self, request, view):
        return get_membership(request.user) is not None


class IsOrgOwnerOrAdmin(BasePermission):
    message = 'Organization owner or admin role required.'

    def has_permission(self, request, view):
        membership = get_membership(request.user)
        if membership is None or membership.role not in (Membership.OWNER, Membership.ADMIN):
            return False
        check_mfa_enrolled(request.user)
        return True
