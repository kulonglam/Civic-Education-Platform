from rest_framework.permissions import BasePermission

from apps.accounts.permissions import check_mfa_enrolled
from apps.accounts.roles import (
    CONTENT_ROLES,
    CONFIG_ROLES,
    LEARNER_ROLES,
    MODERATION_ROLES,
    PLATFORM_ADMIN_ROLES,
    is_platform_admin,
)


class RolePermission(BasePermission):
    allowed_roles: tuple[str, ...] = ()

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Defensive guard: a user with a null role (data integrity slip or
        # mid-migration state) should be denied rather than raise a 500.
        role = getattr(request.user, 'role', None)
        if role is None:
            return False
        if not (getattr(role, 'name', None) in self.allowed_roles):
            return False
        check_mfa_enrolled(request.user)
        return True


class IsAdmin(RolePermission):
    """Administrator or Super Admin — operational control of the civic platform."""

    allowed_roles = tuple(PLATFORM_ADMIN_ROLES)


class IsSuperAdmin(RolePermission):
    """Super Admin — system configuration and security."""

    allowed_roles = tuple(CONFIG_ROLES)


class IsEditor(RolePermission):
    allowed_roles = tuple(CONTENT_ROLES)


class IsModerator(RolePermission):
    allowed_roles = tuple(MODERATION_ROLES)


class IsEditorOrAdmin(RolePermission):
    allowed_roles = tuple(CONTENT_ROLES)


class IsModeratorOrAdmin(RolePermission):
    allowed_roles = tuple(MODERATION_ROLES)


class IsCitizenOrAbove(RolePermission):
    allowed_roles = tuple(LEARNER_ROLES)


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if is_platform_admin(request.user):
            return True
        owner = getattr(obj, 'author', None) or getattr(obj, 'user', None)
        return owner == request.user
