"""Registration, login and logout."""

import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.audit.services import log_activity
from apps.core.branding import PLATFORM_NAME
from apps.core.security import log_security_event
from apps.core.serializers import MessageSerializer
from apps.core.tasks import send_transactional_email, format_mail_error
from apps.core.throttling import AuthRateThrottle

from ..mfa import issue_mfa_challenge, user_has_mfa_enabled, user_requires_mfa
from ..models import EmailVerificationToken
from ..serializers import RegisterSerializer
from ..tokens import EmailTokenObtainPairSerializer

logger = logging.getLogger(__name__)


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
        send_transactional_email(
            f'Verify your {PLATFORM_NAME} account',
            f'Click to verify your email: {verify_url}',
            [user.email],
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_sent = True
        mail_error = ''
        try:
            self.perform_create(serializer)
        except Exception as exc:
            logger.exception('Verification email failed after registration')
            email_sent = False
            mail_error = format_mail_error(exc)
            if serializer.instance is None:
                raise
        message = (
            'Registration successful. Please verify your email.'
            if email_sent
            else (
                'Registration succeeded, but the verification email could not be sent. '
                f'{mail_error} '
                'Set EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, and a Brevo-verified '
                'DEFAULT_FROM_EMAIL on the API service.'
            )
        )
        return Response(
            {'message': message, 'email_sent': email_sent},
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
        revoke_all = bool(request.data.get('revoke_all'))
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        if revoke_all:
            from apps.accounts.session import bump_session_epoch

            bump_session_epoch(request.user)
            log_activity(request.user, 'session_revoked', {'reason': 'logout_all'}, request=request)
        log_activity(request.user, 'user_logout', {})
        return Response({'message': 'Logged out successfully.'})
