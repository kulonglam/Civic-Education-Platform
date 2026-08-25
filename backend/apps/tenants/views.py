from django.contrib.auth import get_user_model
from django.utils import timezone
import logging
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import log_activity
from apps.billing.services import check_quota
from apps.core.branding import PLATFORM_NAME
from apps.core.serializers import MessageSerializer
from apps.core.tasks import send_transactional_email

from .context import get_current_organization
from .models import Membership, Organization, OrganizationInvite
from .permissions import IsOrgMember, IsOrgOwnerOrAdmin
from .serializers import (
    InvitePreviewSerializer,
    MemberInviteSerializer,
    MembershipSerializer,
    MemberRoleUpdateSerializer,
    OrganizationInviteSerializer,
    OrganizationSerializer,
    UserOrganizationMembershipSerializer,
)
from .services import (
    accept_organization_invite,
    create_organization_invite,
    get_valid_invite,
    resolve_department,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class MyOrganizationsView(APIView):
    """List all organizations the authenticated user belongs to (for org switching)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses=UserOrganizationMembershipSerializer(many=True))
    def get(self, request):
        memberships = (
            Membership.objects.filter(user=request.user, organization__is_active=True)
            .select_related('organization')
            .order_by('organization__name')
        )
        serializer = UserOrganizationMembershipSerializer(memberships, many=True)
        return Response(serializer.data)


class CurrentOrganizationView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]
    serializer_class = OrganizationSerializer

    def get(self, request):
        organization = get_current_organization()
        return Response(OrganizationSerializer(organization).data)

    def patch(self, request):
        self.permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]
        self.check_permissions(request)
        organization = get_current_organization()
        serializer = OrganizationSerializer(organization, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_activity(
            request.user,
            'org_settings_changed',
            {'fields': list(serializer.validated_data.keys())},
            organization=organization,
            request=request,
        )
        return Response(serializer.data)


class OrganizationBySlugView(APIView):
    """Public branding lookup for login pages and tenant-specific entry."""

    permission_classes = [AllowAny]
    serializer_class = OrganizationSerializer

    @extend_schema(responses=OrganizationSerializer)
    def get(self, request, slug):
        organization = Organization.objects.filter(slug=slug, is_active=True).first()
        if organization is None:
            return Response({'detail': 'Organization not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrganizationSerializer(organization).data)


class MemberInviteView(APIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]
    serializer_class = MemberInviteSerializer

    @extend_schema(
        request=MemberInviteSerializer,
        responses={
            201: MembershipSerializer,
            202: OrganizationInviteSerializer,
        },
    )
    def post(self, request):
        organization = get_current_organization()
        serializer = MemberInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].lower()
        role = serializer.validated_data['role']
        department = resolve_department(
            organization,
            department_id=serializer.validated_data.get('department_id'),
        )
        if role == Membership.OWNER:
            return Response(
                {'detail': 'Use role transfer to assign ownership.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if OrganizationInvite.objects.filter(
            organization=organization, email=email, accepted_at__isnull=True,
        ).exists():
            return Response(
                {'detail': 'An invitation is already pending for this email.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=email).first()
        if user is not None:
            if Membership.objects.filter(organization=organization, user=user).exists():
                return Response({'detail': 'User is already a member.'}, status=status.HTTP_400_BAD_REQUEST)

            check_quota(organization, 'members')
            membership = Membership.objects.create(
                organization=organization,
                user=user,
                role=role,
                department=department,
            )
            try:
                send_transactional_email(
                    f'You were added to {organization.name}',
                    f'You now have access to "{organization.name}" on {PLATFORM_NAME}.',
                    [email],
                )
            except Exception:
                logger.exception('Member-added email failed for %s', email)
            log_activity(
                request.user,
                'member_invited',
                {'email': email, 'role': role, 'immediate': True},
                organization=organization,
                request=request,
            )
            return Response(MembershipSerializer(membership).data, status=status.HTTP_201_CREATED)

        check_quota(organization, 'members')
        invite = create_organization_invite(
            organization=organization,
            email=email,
            role=role,
            invited_by=request.user,
            department=department,
        )
        log_activity(
            request.user,
            'member_invited',
            {'email': email, 'role': role, 'immediate': False},
            organization=organization,
            request=request,
        )
        return Response(
            OrganizationInviteSerializer(invite).data,
            status=status.HTTP_202_ACCEPTED,
        )


class OrganizationInviteListView(generics.ListAPIView):
    serializer_class = OrganizationInviteSerializer
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]
    pagination_class = None

    def get_queryset(self):
        organization = get_current_organization()
        if organization is None:
            return OrganizationInvite.objects.none()
        return OrganizationInvite.objects.filter(
            organization=organization,
            accepted_at__isnull=True,
            expires_at__gt=timezone.now(),
        )


class OrganizationInviteRevokeView(APIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]

    def delete(self, request, invite_id):
        organization = get_current_organization()
        deleted, _ = OrganizationInvite.objects.filter(
            id=invite_id,
            organization=organization,
            accepted_at__isnull=True,
        ).delete()
        if not deleted:
            return Response({'detail': 'Invite not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvitePreviewView(APIView):
    permission_classes = [AllowAny]
    serializer_class = InvitePreviewSerializer

    @extend_schema(responses=InvitePreviewSerializer)
    def get(self, request, token):
        invite = OrganizationInvite.objects.filter(token=token).select_related('organization').first()
        if invite is None:
            return Response({'detail': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)
        is_expired = not invite.is_pending and invite.accepted_at is None
        if invite.accepted_at is not None:
            return Response({'detail': 'This invitation has already been accepted.'}, status=status.HTTP_410_GONE)
        payload = {
            'email': invite.email,
            'role': invite.role,
            'organization': invite.organization,
            'expires_at': invite.expires_at,
            'is_expired': is_expired,
        }
        return Response(InvitePreviewSerializer(payload).data)


class AcceptInviteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=MembershipSerializer)
    def post(self, request, token):
        invite = get_valid_invite(token)
        if invite is None:
            return Response({'detail': 'Invalid or expired invitation.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            check_quota(invite.organization, 'members')
            membership = accept_organization_invite(invite=invite, user=request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(MembershipSerializer(membership).data, status=status.HTTP_201_CREATED)


class MembershipListView(generics.ListAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated, IsOrgMember]

    def get_queryset(self):
        organization = get_current_organization()
        if organization is None:
            return Membership.objects.none()
        qs = Membership.objects.filter(organization=organization).select_related('user', 'department')
        department_id = self.request.query_params.get('department')
        if department_id:
            qs = qs.filter(department_id=department_id)
        return qs


class MemberDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]
    serializer_class = MemberRoleUpdateSerializer

    def _get_membership(self, request, membership_id):
        organization = get_current_organization()
        return Membership.objects.filter(id=membership_id, organization=organization).first()

    def patch(self, request, membership_id):
        membership = self._get_membership(request, membership_id)
        if membership is None:
            return Response({'detail': 'Member not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MemberRoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_role = serializer.validated_data['role']
        if membership.role == Membership.OWNER and new_role != Membership.OWNER:
            owners = Membership.objects.filter(
                organization=membership.organization, role=Membership.OWNER
            ).count()
            if owners <= 1:
                return Response(
                    {'detail': 'Cannot demote the only owner.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        membership.role = new_role
        if 'department_id' in serializer.validated_data:
            membership.department = resolve_department(
                membership.organization,
                department_id=serializer.validated_data.get('department_id'),
            )
        membership.save()
        log_activity(
            request.user,
            'member_role_changed',
            {'membership_id': str(membership.id), 'role': new_role},
            organization=membership.organization,
            request=request,
        )
        return Response(MembershipSerializer(membership).data)

    def delete(self, request, membership_id):
        membership = self._get_membership(request, membership_id)
        if membership is None:
            return Response({'detail': 'Member not found.'}, status=status.HTTP_404_NOT_FOUND)
        if membership.role == Membership.OWNER:
            owners = Membership.objects.filter(
                organization=membership.organization, role=Membership.OWNER
            ).count()
            if owners <= 1:
                return Response(
                    {'detail': 'Cannot remove the only owner.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        org = membership.organization
        mid = str(membership.id)
        membership.delete()
        log_activity(
            request.user,
            'member_removed',
            {'membership_id': mid},
            organization=org,
            request=request,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class LeaveOrganizationView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]
    serializer_class = MessageSerializer

    @extend_schema(request=None, responses=MessageSerializer)
    def post(self, request):
        organization = get_current_organization()
        membership = Membership.objects.filter(organization=organization, user=request.user).first()
        if membership is None:
            return Response({'detail': 'Not a member.'}, status=status.HTTP_404_NOT_FOUND)
        if membership.role == Membership.OWNER:
            owners = Membership.objects.filter(organization=organization, role=Membership.OWNER).count()
            if owners <= 1:
                return Response(
                    {'detail': 'Transfer ownership before leaving.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        membership.delete()
        return Response({'message': 'You have left the organization.'})
