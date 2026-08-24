"""Moderator and admin actions on other users."""

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import log_activity
from apps.core.permissions import IsAdmin, IsModeratorOrAdmin
from apps.core.serializers import MessageSerializer

from ..models import Role
from ..serializers import UserRoleUpdateSerializer, UserSerializer

User = get_user_model()


def _get_managed_user(request, user_id):
    """Resolve a user visible in the current admin/moderator list."""
    from apps.tenants.context import get_current_organization
    from apps.tenants.models import Membership

    try:
        user = User.objects.select_related('role').get(pk=user_id)
    except User.DoesNotExist:
        return None
    organization = get_current_organization()
    if organization is not None and not Membership.objects.filter(
        organization=organization,
        user=user,
    ).exists():
        return None
    return user


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsModeratorOrAdmin]

    def get_queryset(self):
        from apps.tenants.context import get_current_organization

        qs = User.objects.select_related('role', 'profile')
        organization = get_current_organization()
        if organization is not None:
            qs = qs.filter(memberships__organization=organization).distinct()
        return qs


class SuspendUserView(APIView):
    permission_classes = [IsModeratorOrAdmin]

    @extend_schema(request=None, responses=MessageSerializer)
    def post(self, request, user_id):
        user = _get_managed_user(request, user_id)
        if user is None:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        user.is_suspended = True
        user.save(update_fields=['is_suspended'])
        from apps.accounts.session import bump_session_epoch

        bump_session_epoch(user)
        log_activity(request.user, 'user_suspended', {'target_user_id': str(user.id)})
        return Response({'message': f'User {user.email} suspended.'})


class UnsuspendUserView(APIView):
    permission_classes = [IsModeratorOrAdmin]

    @extend_schema(request=None, responses=MessageSerializer)
    def post(self, request, user_id):
        user = _get_managed_user(request, user_id)
        if user is None:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        user.is_suspended = False
        user.save(update_fields=['is_suspended'])
        log_activity(request.user, 'user_unsuspended', {'target_user_id': str(user.id)})
        return Response({'message': f'User {user.email} reactivated.'})


class UpdateUserRoleView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(request=UserRoleUpdateSerializer, responses=UserSerializer)
    def patch(self, request, user_id):
        if str(request.user.id) == str(user_id):
            return Response(
                {'detail': 'You cannot change your own role.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = _get_managed_user(request, user_id)
        if user is None:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserRoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role_name = serializer.validated_data['role']
        if user.role.name == role_name:
            return Response(UserSerializer(user).data)

        role = Role.objects.get(name=role_name)
        previous_role = user.role.name
        user.role = role
        user.save(update_fields=['role'])
        log_activity(
            request.user,
            'user_role_changed',
            {
                'target_user_id': str(user.id),
                'previous_role': previous_role,
                'new_role': role_name,
            },
        )
        return Response(UserSerializer(user).data)
