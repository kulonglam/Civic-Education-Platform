import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.audit.services import log_activity
from apps.core.permissions import IsAdmin, IsModeratorOrAdmin
from apps.core.security import log_security_event
from apps.core.serializers import MessageSerializer
from apps.core.storage import upload_file
from apps.core.tasks import send_email_task
from apps.core.throttling import AuthRateThrottle

from .models import EmailVerificationToken, Role
from .mfa import (
    consume_mfa_challenge,
    generate_totp_secret,
    issue_mfa_challenge,
    provisioning_uri,
    user_has_mfa_enabled,
    user_requires_mfa,
    verify_totp_code,
)
from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetOtpConfirmSerializer,
    PasswordResetOtpRequestSerializer,
    PasswordResetRequestSerializer,
    PhoneVerifyConfirmSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserRoleUpdateSerializer,
    UserSerializer,
)
from .tokens import EmailTokenObtainPairSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def perform_create(self, serializer):
        user = serializer.save()
        self._send_verification_email(user)
        log_activity(user, 'user_registered', {'email': user.email})

    def _send_verification_email(self, user):
        token = secrets.token_urlsafe(32)
        EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(hours=24),
        )
        verify_url = f'{settings.FRONTEND_URL}/verify-email/{token}'
        send_email_task.delay(
            'Verify your Civic Education Platform account',
            f'Click to verify your email: {verify_url}',
            [user.email],
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'message': 'Registration successful. Please verify your email.'},
            status=status.HTTP_201_CREATED,
        )


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class LoginView(EmailTokenObtainPairView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            log_security_event(
                'login_failed',
                request=request,
                detail={'email': request.data.get('email')},
            )
            raise

        user = serializer.user
        if user.is_suspended:
            log_security_event('login_blocked_suspended', request=request, user=user)
            return Response(
                {'detail': 'Account suspended.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        requires_mfa = user_requires_mfa(user)
        mfa_enabled = user_has_mfa_enabled(user)

        if requires_mfa and mfa_enabled:
            mfa_token = issue_mfa_challenge(user)
            log_security_event('login_mfa_challenge_issued', request=request, user=user)
            return Response(
                {
                    'mfa_required': True,
                    'mfa_token': mfa_token,
                    'mfa_setup_required': False,
                },
                status=status.HTTP_200_OK,
            )

        log_security_event('login_success', request=request, user=user)
        log_activity(user, 'user_login', {'email': user.email})

        data = dict(serializer.validated_data)
        if requires_mfa and not mfa_enabled:
            data['mfa_setup_required'] = True
        return Response(data, status=status.HTTP_200_OK)


class MfaSetupView(APIView):
    """Begin or complete TOTP enrollment for privileged accounts."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthRateThrottle]

    @extend_schema(responses=inline_serializer(
        name='MfaSetupResponse',
        fields={
            'secret': serializers.CharField(),
            'provisioning_uri': serializers.CharField(),
        },
    ))
    def get(self, request):
        if user_has_mfa_enabled(request.user):
            return Response(
                {'detail': 'Multi-factor authentication is already enabled.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        secret = generate_totp_secret()
        cache.set(f'mfa:setup:{request.user.pk}', secret, timeout=600)
        return Response({
            'secret': secret,
            'provisioning_uri': provisioning_uri(request.user, secret),
        })

    @extend_schema(
        request=inline_serializer(
            name='MfaSetupConfirmRequest',
            fields={'code': serializers.CharField(max_length=6)},
        ),
        responses=MessageSerializer,
    )
    def post(self, request):
        code = (request.data.get('code') or '').strip()
        secret = cache.get(f'mfa:setup:{request.user.pk}')
        if not secret:
            return Response(
                {'detail': 'MFA setup expired. Request a new setup code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not verify_totp_code(secret, code):
            log_security_event('mfa_setup_failed', request=request, user=request.user)
            return Response(
                {'detail': 'Invalid verification code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profile = request.user.profile
        profile.totp_secret = secret
        profile.mfa_enabled = True
        profile.save(update_fields=['totp_secret', 'mfa_enabled'])
        cache.delete(f'mfa:setup:{request.user.pk}')
        log_security_event('mfa_enabled', request=request, user=request.user)
        return Response({'message': 'Multi-factor authentication enabled.'})


class MfaVerifyLoginView(APIView):
    """Complete login after password verification with a TOTP code."""

    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    @extend_schema(
        request=inline_serializer(
            name='MfaVerifyLoginRequest',
            fields={
                'mfa_token': serializers.CharField(),
                'code': serializers.CharField(max_length=6),
            },
        ),
    )
    def post(self, request):
        mfa_token = (request.data.get('mfa_token') or '').strip()
        code = (request.data.get('code') or '').strip()
        user = consume_mfa_challenge(mfa_token)
        if user is None:
            log_security_event(
                'mfa_verify_failed',
                request=request,
                detail={'reason': 'invalid_or_expired_token'},
            )
            return Response(
                {'detail': 'Invalid or expired MFA session. Please sign in again.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not verify_totp_code(user.profile.totp_secret, code):
            log_security_event('mfa_verify_failed', request=request, user=user)
            return Response(
                {'detail': 'Invalid verification code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = EmailTokenObtainPairSerializer.get_token(user)
        log_security_event('login_success', request=request, user=user, detail={'mfa': True})
        log_activity(user, 'user_login', {'email': user.email, 'mfa': True})
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=inline_serializer(
            name='LogoutRequest',
            fields={'refresh': serializers.CharField()},
        ),
        responses=MessageSerializer,
    )
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        log_activity(request.user, 'user_logout', {})
        return Response({'message': 'Logged out successfully.'})


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses=MessageSerializer)
    def get(self, request, token):
        try:
            verification = EmailVerificationToken.objects.select_related('user').get(
                token=token, used=False, expires_at__gt=timezone.now()
            )
        except EmailVerificationToken.DoesNotExist:
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
        user = verification.user
        user.email_verified = True
        user.save(update_fields=['email_verified'])
        verification.used = True
        verification.save(update_fields=['used'])
        log_activity(user, 'email_verified', {})
        return Response({'message': 'Email verified successfully.'})


class ResendVerificationEmailView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthRateThrottle]

    @extend_schema(responses=MessageSerializer)
    def post(self, request):
        user = request.user
        if user.email_verified:
            return Response({'message': 'Email is already verified.'})
        token = secrets.token_urlsafe(32)
        EmailVerificationToken.objects.filter(user=user, used=False).update(used=True)
        EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(hours=24),
        )
        verify_url = f'{settings.FRONTEND_URL}/verify-email/{token}'
        send_email_task.delay(
            'Verify your Civic Education Platform account',
            f'Click to verify your email: {verify_url}',
            [user.email],
        )
        return Response({'message': 'Verification email sent.'})


class PhoneVerifySendView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthRateThrottle]

    @extend_schema(responses=MessageSerializer)
    def post(self, request):
        user = request.user
        if not user.phone:
            return Response(
                {'detail': 'Add a phone number to your profile first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.phone_verified:
            return Response({'message': 'Phone number is already verified.'})
        from apps.notifications.sms_services import send_phone_verify_otp

        send_phone_verify_otp(user)
        return Response({'message': 'Verification code sent to your phone.'})


class PhoneVerifyConfirmView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthRateThrottle]

    @extend_schema(request=PhoneVerifyConfirmSerializer, responses=MessageSerializer)
    def post(self, request):
        serializer = PhoneVerifyConfirmSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.phone_verified = True
        user.save(update_fields=['phone_verified'])
        log_activity(user, 'admin_action', {'action': 'phone_verified'})
        return Response({'message': 'Phone number verified successfully.'})


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    serializer_class = PasswordResetRequestSerializer

    @extend_schema(request=PasswordResetRequestSerializer, responses=MessageSerializer)
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        if user:
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.encoding import force_bytes
            from django.utils.http import urlsafe_base64_encode

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f'{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}'
            send_email_task.delay(
                'Reset your password',
                f'Click to reset your password: {reset_url}',
                [user.email],
            )
            from apps.notifications.sms_services import send_password_reset_otp

            send_password_reset_otp(user)
        return Response({'message': 'If the email exists, a reset link has been sent.'})


class PasswordResetOtpRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    serializer_class = PasswordResetOtpRequestSerializer

    @extend_schema(request=PasswordResetOtpRequestSerializer, responses=MessageSerializer)
    def post(self, request):
        serializer = PasswordResetOtpRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from apps.notifications.sms_services import normalize_phone, send_password_reset_otp

        phone = normalize_phone(serializer.validated_data['phone'])
        user = User.objects.filter(phone=phone).first()
        if user:
            send_password_reset_otp(user)
        return Response({'message': 'If the phone number exists, a verification code has been sent.'})


class PasswordResetOtpConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    serializer_class = PasswordResetOtpConfirmSerializer

    @extend_schema(request=PasswordResetOtpConfirmSerializer, responses=MessageSerializer)
    def post(self, request):
        serializer = PasswordResetOtpConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log_activity(user, 'password_reset', {'via': 'sms_otp'})
        return Response({'message': 'Password reset successful.'})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    serializer_class = PasswordResetConfirmSerializer

    @extend_schema(request=PasswordResetConfirmSerializer, responses=MessageSerializer)
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log_activity(user, 'password_reset', {})
        return Response({'message': 'Password reset successful.'})


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


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ProfileUpdateSerializer
        return UserSerializer

    def retrieve(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data)

    def update(self, request, *args, **kwargs):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=inline_serializer(
            name='AvatarUploadRequest',
            fields={'avatar': serializers.ImageField()},
        ),
        responses=inline_serializer(
            name='AvatarUploadResponse',
            fields={'avatar_url': serializers.CharField()},
        ),
    )
    def patch(self, request):
        file = request.FILES.get('avatar')
        if not file:
            return Response({'detail': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        path = f'avatars/{request.user.id}/{file.name}'
        url = upload_file(path, file.read(), file.content_type)
        if url:
            profile = request.user.profile
            profile.avatar_url = url
            profile.save(update_fields=['avatar_url'])
        return Response({'avatar_url': request.user.profile.avatar_url})


class SuspendUserView(APIView):
    permission_classes = [IsModeratorOrAdmin]

    @extend_schema(request=None, responses=MessageSerializer)
    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        user.is_suspended = True
        user.save(update_fields=['is_suspended'])
        log_activity(request.user, 'user_suspended', {'target_user_id': str(user.id)})
        return Response({'message': f'User {user.email} suspended.'})


class UnsuspendUserView(APIView):
    permission_classes = [IsModeratorOrAdmin]

    @extend_schema(request=None, responses=MessageSerializer)
    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        user.is_suspended = False
        user.save(update_fields=['is_suspended'])
        log_activity(request.user, 'user_unsuspended', {'target_user_id': str(user.id)})
        return Response({'message': f'User {user.email} reactivated.'})


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


class ChangePasswordView(APIView):
    """Allow an authenticated user to change their own password."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthRateThrottle]

    @extend_schema(
        request=inline_serializer(
            name='ChangePasswordRequest',
            fields={
                'current_password': serializers.CharField(),
                'new_password': serializers.CharField(min_length=8),
            },
        ),
        responses=MessageSerializer,
    )
    def post(self, request):
        current_password = request.data.get('current_password', '')
        new_password = request.data.get('new_password', '')

        if not current_password or not new_password:
            return Response(
                {'detail': 'Both current_password and new_password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(new_password) < 8:
            return Response(
                {'detail': 'New password must be at least 8 characters.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.check_password(current_password):
            return Response(
                {'detail': 'Current password is incorrect.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(new_password)
        request.user.save(update_fields=['password'])
        log_activity(request.user, 'password_changed', {})
        return Response({'message': 'Password updated successfully.'})


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


class MfaSetupView(APIView):
    """Begin or complete TOTP enrollment for privileged accounts."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthRateThrottle]

    @extend_schema(responses=inline_serializer(
        name='MfaSetupResponse',
        fields={
            'secret': serializers.CharField(),
            'provisioning_uri': serializers.CharField(),
        },
    ))
    def get(self, request):
        if user_has_mfa_enabled(request.user):
            return Response(
                {'detail': 'Multi-factor authentication is already enabled.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        secret = generate_totp_secret()
        cache.set(f'mfa:setup:{request.user.pk}', secret, timeout=600)
        return Response({
            'secret': secret,
            'provisioning_uri': provisioning_uri(request.user, secret),
        })

    @extend_schema(
        request=inline_serializer(
            name='MfaSetupConfirmRequest',
            fields={'code': serializers.CharField(max_length=6, min_length=6)},
        ),
        responses=MessageSerializer,
    )
    def post(self, request):
        code = str(request.data.get('code', '')).strip()
        secret = cache.get(f'mfa:setup:{request.user.pk}')
        if not secret:
            return Response(
                {'detail': 'MFA setup expired. Request a new setup code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not verify_totp_code(secret, code):
            log_security_event('mfa_setup_failed', request=request, user=request.user)
            return Response(
                {'detail': 'Invalid verification code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = request.user.profile
        profile.totp_secret = secret
        profile.mfa_enabled = True
        profile.save(update_fields=['totp_secret', 'mfa_enabled'])
        cache.delete(f'mfa:setup:{request.user.pk}')
        log_security_event('mfa_enabled', request=request, user=request.user)
        log_activity(request.user, 'mfa_enabled', {})
        return Response({'message': 'Multi-factor authentication enabled.'})


class MfaVerifyLoginView(APIView):
    """Complete login after password verification when MFA is enabled."""

    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    @extend_schema(
        request=inline_serializer(
            name='MfaVerifyLoginRequest',
            fields={
                'mfa_token': serializers.CharField(),
                'code': serializers.CharField(max_length=6, min_length=6),
            },
        ),
    )
    def post(self, request):
        mfa_token = request.data.get('mfa_token', '')
        code = str(request.data.get('code', '')).strip()
        user = consume_mfa_challenge(mfa_token)
        if user is None:
            log_security_event(
                'mfa_verify_failed',
                request=request,
                detail={'reason': 'invalid_or_expired_token'},
            )
            return Response(
                {'detail': 'Invalid or expired MFA session. Please sign in again.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not verify_totp_code(user.profile.totp_secret, code):
            log_security_event('mfa_verify_failed', request=request, user=user)
            return Response(
                {'detail': 'Invalid verification code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = EmailTokenObtainPairSerializer.get_token(user)
        log_security_event('login_success', request=request, user=user, detail={'mfa': True})
        log_activity(user, 'user_login', {'email': user.email, 'mfa': True})
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
