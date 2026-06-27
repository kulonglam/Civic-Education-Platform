from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import log_activity
from apps.billing.services import plan_has_sso, require_sso
from apps.tenants.models import Organization

from . import sso


class SsoStatusView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: dict})
    def get(self, request):
        org_slug = request.query_params.get('org') or request.headers.get('X-Tenant-Slug')
        organization = None
        enabled_for_org = False
        if org_slug:
            organization = Organization.objects.filter(slug=org_slug, is_active=True).first()
            if organization:
                enabled_for_org = plan_has_sso(organization)

        configured = sso.oidc_configured()
        login_path = None
        if configured and enabled_for_org and org_slug:
            login_path = f'/api/auth/sso/login/?{urlencode({"org": org_slug})}'

        return Response(
            {
                'configured': configured,
                'enabled_for_org': enabled_for_org,
                'organization': org_slug,
                'login_path': login_path,
            }
        )


class SsoLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if not sso.oidc_configured():
            return Response(
                {'detail': 'SSO is not configured on this server.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        org_slug = request.query_params.get('org')
        if not org_slug:
            return Response({'detail': 'Organization slug is required.'}, status=status.HTTP_400_BAD_REQUEST)

        organization = get_object_or_404(Organization, slug=org_slug, is_active=True)
        require_sso(organization)

        try:
            # build_authorize_url now returns (url, state) — state is already
            # persisted in cache by store_sso_state() inside the helper.
            authorize_url, _state = sso.build_authorize_url(org_slug)
        except Exception as exc:
            return Response(
                {'detail': f'Could not start SSO login: {exc}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return HttpResponseRedirect(authorize_url)


class SsoCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        error = request.query_params.get('error')
        if error:
            params = urlencode({'error': request.query_params.get('error_description', error)})
            return HttpResponseRedirect(f'{settings.FRONTEND_URL.rstrip("/")}/sso/callback?{params}')

        code = request.query_params.get('code')
        state = request.query_params.get('state')
        if not code or not state:
            return Response({'detail': 'Missing authorization code.'}, status=status.HTTP_400_BAD_REQUEST)

        state_payload = sso.pop_sso_state(state)
        if state_payload is None:
            return Response({'detail': 'Invalid or expired SSO state.'}, status=status.HTTP_400_BAD_REQUEST)

        org_slug = state_payload.get('org_slug')
        # Retrieve nonce stored at login time for replay-attack prevention
        nonce = state_payload.get('nonce')

        try:
            token_payload = sso.exchange_code_for_tokens(code)
            # Pass nonce so _verify_id_token can validate it against the id_token claim
            claims = sso.claims_from_tokens(token_payload, nonce=nonce)
            user = sso.get_or_create_user_from_sso(claims, org_slug)
            tokens = sso.issue_jwt_tokens(user)
            log_activity(user, 'user_login', {'email': user.email, 'method': 'sso'})
        except ValueError as exc:
            params = urlencode({'error': str(exc)})
            return HttpResponseRedirect(f'{settings.FRONTEND_URL.rstrip("/")}/sso/callback?{params}')
        except Exception as exc:
            logger_msg = f'SSO login failed: {exc}'
            return Response(
                {'detail': logger_msg},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Tokens are placed in the URL *fragment* (hash), not query params,
        # to avoid leakage in server logs and Referer headers.
        return HttpResponseRedirect(sso.frontend_callback_url(tokens, org_slug=org_slug))
