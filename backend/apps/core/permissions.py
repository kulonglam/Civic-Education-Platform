from rest_framework.permissions import BasePermission

from apps.accounts.permissions import check_mfa_enrolled


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
    """Platform administrator — cross-tenant ops, analytics, role assignment."""

    allowed_roles = ('admin',)


class IsEditor(RolePermission):
    allowed_roles = ('editor', 'admin')


class IsModerator(RolePermission):
    allowed_roles = ('moderator', 'admin')


class IsEditorOrAdmin(RolePermission):
    allowed_roles = ('editor', 'admin')


class IsModeratorOrAdmin(RolePermission):
    allowed_roles = ('moderator', 'admin')


class IsCitizenOrAbove(RolePermission):
    allowed_roles = ('citizen', 'moderator', 'editor', 'admin')


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        role = getattr(request.user, 'role', None)
        if getattr(role, 'name', None) == 'admin':
            return True
        owner = getattr(obj, 'author', None) or getattr(obj, 'user', None)
        return owner == request.user
