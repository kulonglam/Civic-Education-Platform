"""Cookie-aware JWT refresh — accepts refresh from body or httpOnly cookie."""

from django.conf import settings
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView


class CookieAwareTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        refresh = (attrs.get('refresh') or '').strip() or None
        if not refresh:
            request = self.context.get('request')
            cookie_name = getattr(settings, 'JWT_REFRESH_COOKIE', 'cep_refresh')
            refresh = request.COOKIES.get(cookie_name) if request is not None else None
        if not refresh:
            raise serializers.ValidationError(
                {'refresh': 'No refresh token provided in body or cookie.'}
            )
        try:
            token = RefreshToken(refresh)
        except TokenError as exc:
            raise InvalidToken(exc.args[0]) from exc

        data = {'access': str(token.access_token)}
        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    from rest_framework_simplejwt.token_blacklist.models import (
                        BlacklistedToken,
                        OutstandingToken,
                    )

                    outstanding = OutstandingToken.objects.get(jti=token['jti'])
                    BlacklistedToken.objects.get_or_create(token=outstanding)
                except Exception:  # noqa: BLE001
                    pass
            token.set_jti()
            token.set_exp()
            token.set_iat()
            if hasattr(token, 'outstand'):
                token.outstand()
            data['refresh'] = str(token)
        return data


class CookieTokenRefreshView(TokenRefreshView):
    """Refresh access tokens using body or the httpOnly refresh cookie."""

    serializer_class = CookieAwareTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(exc.args[0]) from exc
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
