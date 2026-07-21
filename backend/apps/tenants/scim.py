"""SCIM 2.0 Users provisioning (subset) for enterprise IdP sync."""

from __future__ import annotations

import hashlib
import re
import secrets
import uuid

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Role, UserProfile
from apps.accounts.session import bump_session_epoch
from apps.audit.services import log_activity
from apps.tenants.models import Membership, OrganizationScimToken

User = get_user_model()

SCIM_CONTENT_TYPE = 'application/scim+json'


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def authenticate_scim(request) -> OrganizationScimToken | None:
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    raw = auth.split(' ', 1)[1].strip()
    if not raw:
        return None
    token = (
        OrganizationScimToken.objects.select_related('organization')
        .filter(token_hash=_hash_token(raw), is_active=True)
        .first()
    )
    if token is None:
        return None
    OrganizationScimToken.objects.filter(pk=token.pk).update(last_used_at=timezone.now())
    return token


def _scim_error(status_code: int, detail: str, scim_type: str = 'invalidRequest'):
    return Response(
        {
            'schemas': ['urn:ietf:params:scim:api:messages:2.0:Error'],
            'detail': detail,
            'status': str(status_code),
            'scimType': scim_type,
        },
        status=status_code,
        content_type=SCIM_CONTENT_TYPE,
    )


def _user_to_scim(user, organization) -> dict:
    membership = Membership.objects.filter(organization=organization, user=user).first()
    return {
        'schemas': ['urn:ietf:params:scim:schemas:core:2.0:User'],
        'id': str(user.id),
        'userName': user.email,
        'name': {
            'givenName': user.first_name,
            'familyName': user.last_name,
            'formatted': user.full_name,
        },
        'emails': [{'value': user.email, 'primary': True, 'type': 'work'}],
        'active': bool(user.is_active and not user.is_suspended and membership is not None),
        'meta': {
            'resourceType': 'User',
            'created': user.created_at.isoformat() if user.created_at else None,
            'lastModified': user.updated_at.isoformat() if user.updated_at else None,
        },
    }


def _parse_filter_username(filter_expr: str | None) -> str | None:
    if not filter_expr:
        return None
    match = re.search(
        r'userName\s+eq\s+"([^"]+)"',
        filter_expr,
        flags=re.IGNORECASE,
    )
    return match.group(1).strip().lower() if match else None


class ScimUsersView(APIView):
    """SCIM Users collection: list/filter and create."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        scim = authenticate_scim(request)
        if scim is None:
            return _scim_error(401, 'Unauthorized', 'invalidToken')
        org = scim.organization
        username = _parse_filter_username(request.query_params.get('filter'))
        memberships = Membership.objects.filter(organization=org).select_related('user')
        if username:
            memberships = memberships.filter(user__email__iexact=username)
        start = max(int(request.query_params.get('startIndex', 1) or 1), 1)
        count = min(int(request.query_params.get('count', 100) or 100), 200)
        total = memberships.count()
        page = list(memberships[start - 1:start - 1 + count])
        resources = [_user_to_scim(m.user, org) for m in page]
        return Response(
            {
                'schemas': ['urn:ietf:params:scim:api:messages:2.0:ListResponse'],
                'totalResults': total,
                'startIndex': start,
                'itemsPerPage': len(resources),
                'Resources': resources,
            },
            content_type=SCIM_CONTENT_TYPE,
        )

    def post(self, request):
        scim = authenticate_scim(request)
        if scim is None:
            return _scim_error(401, 'Unauthorized', 'invalidToken')
        org = scim.organization
        data = request.data if isinstance(request.data, dict) else {}
        email = (data.get('userName') or '').strip().lower()
        if not email and data.get('emails'):
            email = str(data['emails'][0].get('value', '')).strip().lower()
        if not email:
            return _scim_error(400, 'userName (email) is required')

        name = data.get('name') or {}
        first_name = (name.get('givenName') or email.split('@')[0])[:150]
        last_name = (name.get('familyName') or 'User')[:150]
        active = data.get('active', True)

        user = User.objects.filter(email__iexact=email).first()
        created = False
        if user is None:
            role, _ = Role.objects.get_or_create(name=Role.CITIZEN)
            user = User.objects.create_user(
                email=email,
                password=secrets.token_urlsafe(32),
                first_name=first_name,
                last_name=last_name,
                role=role,
            )
            user.email_verified = True
            user.is_active = bool(active)
            user.save(update_fields=['email_verified', 'is_active'])
            UserProfile.objects.get_or_create(user=user)
            created = True
        else:
            user.first_name = first_name or user.first_name
            user.last_name = last_name or user.last_name
            user.is_active = bool(active)
            user.save(update_fields=['first_name', 'last_name', 'is_active', 'updated_at'])

        Membership.objects.get_or_create(
            organization=org,
            user=user,
            defaults={'role': Membership.MEMBER},
        )
        log_activity(
            user,
            'scim_user_provisioned',
            {'email': email, 'created': created},
            organization=org,
            request=request,
        )
        return Response(
            _user_to_scim(user, org),
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            content_type=SCIM_CONTENT_TYPE,
        )


class ScimUserDetailView(APIView):
    """SCIM User resource: get / patch / deactivate."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def _resolve(self, request, user_id):
        scim = authenticate_scim(request)
        if scim is None:
            return None, _scim_error(401, 'Unauthorized', 'invalidToken')
        try:
            uid = uuid.UUID(str(user_id))
        except ValueError:
            return None, _scim_error(404, 'User not found')
        membership = (
            Membership.objects.select_related('user')
            .filter(organization=scim.organization, user_id=uid)
            .first()
        )
        if membership is None:
            return None, _scim_error(404, 'User not found')
        return (scim, membership), None

    def get(self, request, user_id):
        resolved, err = self._resolve(request, user_id)
        if err:
            return err
        scim, membership = resolved
        return Response(
            _user_to_scim(membership.user, scim.organization),
            content_type=SCIM_CONTENT_TYPE,
        )

    def patch(self, request, user_id):
        resolved, err = self._resolve(request, user_id)
        if err:
            return err
        scim, membership = resolved
        user = membership.user
        data = request.data if isinstance(request.data, dict) else {}
        ops = data.get('Operations') or []
        for op in ops:
            path = (op.get('path') or '').lower()
            value = op.get('value')
            op_type = (op.get('op') or 'replace').lower()
            if op_type not in ('replace', 'add'):
                continue
            if path == 'active' or (not path and isinstance(value, dict) and 'active' in value):
                active = value if path == 'active' else value.get('active')
                user.is_active = bool(active)
                if not active:
                    bump_session_epoch(user)
                    membership.delete()
                    log_activity(
                        user,
                        'scim_user_deactivated',
                        {'email': user.email},
                        organization=scim.organization,
                        request=request,
                    )
                    user.save(update_fields=['is_active', 'updated_at'])
                    return Response(
                        _user_to_scim(user, scim.organization),
                        content_type=SCIM_CONTENT_TYPE,
                    )
            if path.startswith('name.') or path == 'name':
                name_val = value if path == 'name' else None
                if path == 'name.givenname':
                    user.first_name = str(value)[:150]
                elif path == 'name.familyname':
                    user.last_name = str(value)[:150]
                elif isinstance(name_val, dict):
                    if name_val.get('givenName'):
                        user.first_name = str(name_val['givenName'])[:150]
                    if name_val.get('familyName'):
                        user.last_name = str(name_val['familyName'])[:150]
            if not path and isinstance(value, dict):
                if 'active' in value:
                    user.is_active = bool(value['active'])
                name_val = value.get('name') or {}
                if name_val.get('givenName'):
                    user.first_name = str(name_val['givenName'])[:150]
                if name_val.get('familyName'):
                    user.last_name = str(name_val['familyName'])[:150]
        user.save(update_fields=['first_name', 'last_name', 'is_active', 'updated_at'])
        log_activity(
            user,
            'scim_user_updated',
            {'email': user.email},
            organization=scim.organization,
            request=request,
        )
        return Response(
            _user_to_scim(user, scim.organization),
            content_type=SCIM_CONTENT_TYPE,
        )

    def delete(self, request, user_id):
        resolved, err = self._resolve(request, user_id)
        if err:
            return err
        scim, membership = resolved
        user = membership.user
        membership.delete()
        bump_session_epoch(user)
        log_activity(
            user,
            'scim_user_deactivated',
            {'email': user.email, 'method': 'DELETE'},
            organization=scim.organization,
            request=request,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
