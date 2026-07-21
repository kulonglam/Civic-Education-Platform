from rest_framework.permissions import BasePermission

from apps.accounts.permissions import check_mfa_enrolled

from .context import get_current_organization
from .models import Membership


def get_membership(user):
    organization = get_current_organization()
    if organization is None or not user or not user.is_authenticated:
        return None
    return Membership.objects.filter(organization=organization, user=user).first()


def _platform_role_name(user) -> str | None:
    role = getattr(user, 'role', None)
    return getattr(role, 'name', None) if role is not None else None


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


class IsOrgContentEditor(BasePermission):
    """Articles/quizzes: platform editor/admin OR org owner/admin/content_manager."""

    message = 'Content editor role required.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if _platform_role_name(user) in ('editor', 'admin'):
            check_mfa_enrolled(user)
            return True
        membership = get_membership(user)
        if membership and membership.role in (
            Membership.OWNER,
            Membership.ADMIN,
            Membership.CONTENT_MANAGER,
        ):
            if membership.role in (Membership.OWNER, Membership.ADMIN):
                check_mfa_enrolled(user)
            return True
        return False


class IsOrgForumModerator(BasePermission):
    """Forum moderation: platform moderator/admin OR org owner/admin/moderator."""

    message = 'Forum moderator role required.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if _platform_role_name(user) in ('moderator', 'admin'):
            check_mfa_enrolled(user)
            return True
        membership = get_membership(user)
        if membership and membership.role in (
            Membership.OWNER,
            Membership.ADMIN,
            Membership.MODERATOR,
        ):
            if membership.role in (Membership.OWNER, Membership.ADMIN):
                check_mfa_enrolled(user)
            return True
        return False


class CanDeleteOrgContent(BasePermission):
    """Destructive content ops: platform admin OR org owner/admin."""

    message = 'Organization owner/admin or platform admin required to delete.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if _platform_role_name(user) == 'admin':
            check_mfa_enrolled(user)
            return True
        membership = get_membership(user)
        if membership and membership.role in (Membership.OWNER, Membership.ADMIN):
            check_mfa_enrolled(user)
            return True
        return False
