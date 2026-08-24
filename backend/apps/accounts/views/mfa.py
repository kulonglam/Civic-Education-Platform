"""TOTP enrollment and the second login factor.

Imports the TOTP helpers absolutely so they are not confused with this module,
which shares its name with ``apps.accounts.mfa``.
"""

from django.core.cache import cache
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.mfa import (
    consume_mfa_challenge,
    generate_totp_secret,
    provisioning_uri,
    user_has_mfa_enabled,
    verify_totp_code,
)
from apps.accounts.tokens import EmailTokenObtainPairSerializer
from apps.audit.services import log_activity
from apps.core.security import log_security_event
from apps.core.serializers import MessageSerializer
from apps.core.throttling import AuthRateThrottle


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
