"""SCIM 2.0 Groups — mapped to organization departments."""

from __future__ import annotations

import uuid

from django.utils.text import slugify
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import log_activity
from apps.tenants.models import Department, Membership

from .scim import SCIM_CONTENT_TYPE, _scim_error, authenticate_scim


def _group_to_scim(department: Department) -> dict:
    members = list(
        Membership.objects.filter(department=department)
        .select_related('user')
        .values_list('user_id', flat=True)
    )
    return {
        'schemas': ['urn:ietf:params:scim:schemas:core:2.0:Group'],
        'id': str(department.id),
        'displayName': department.name,
        'members': [{'value': str(uid), 'type': 'User'} for uid in members],
        'meta': {
            'resourceType': 'Group',
            'created': department.created_at.isoformat() if department.created_at else None,
        },
    }


class ScimGroupsView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        scim = authenticate_scim(request)
        if scim is None:
            return _scim_error(401, 'Unauthorized', 'invalidToken')
        org = scim.organization
        departments = Department.objects.filter(organization=org).order_by('name')
        start = max(int(request.query_params.get('startIndex', 1) or 1), 1)
        count = min(int(request.query_params.get('count', 100) or 100), 200)
        total = departments.count()
        page = list(departments[start - 1:start - 1 + count])
        resources = [_group_to_scim(d) for d in page]
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
        name = (data.get('displayName') or '').strip()
        if not name:
            return _scim_error(400, 'displayName is required')
        base_slug = slugify(name)[:140] or 'department'
        slug = base_slug
        n = 1
        while Department.objects.filter(organization=org, slug=slug).exists():
            n += 1
            slug = f'{base_slug}-{n}'
        department = Department.objects.create(organization=org, name=name[:150], slug=slug)
        log_activity(
            None,
            'admin_action',
            {'action': 'scim_group_created', 'department': name},
            organization=org,
            request=request,
        )
        return Response(
            _group_to_scim(department),
            status=status.HTTP_201_CREATED,
            content_type=SCIM_CONTENT_TYPE,
        )


class ScimGroupDetailView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def _resolve(self, request, group_id):
        scim = authenticate_scim(request)
        if scim is None:
            return None, _scim_error(401, 'Unauthorized', 'invalidToken')
        try:
            gid = uuid.UUID(str(group_id))
        except ValueError:
            return None, _scim_error(404, 'Group not found')
        department = Department.objects.filter(organization=scim.organization, id=gid).first()
        if department is None:
            return None, _scim_error(404, 'Group not found')
        return (scim, department), None

    def get(self, request, group_id):
        resolved, err = self._resolve(request, group_id)
        if err:
            return err
        _, department = resolved
        return Response(_group_to_scim(department), content_type=SCIM_CONTENT_TYPE)

    def patch(self, request, group_id):
        resolved, err = self._resolve(request, group_id)
        if err:
            return err
        scim, department = resolved
        data = request.data if isinstance(request.data, dict) else {}
        for op in data.get('Operations') or []:
            path = (op.get('path') or '').lower()
            value = op.get('value')
            if path == 'displayname' or (not path and isinstance(value, dict) and 'displayName' in value):
                name = value if path == 'displayname' else value.get('displayName')
                if name:
                    department.name = str(name)[:150]
                    department.save(update_fields=['name'])
            if path == 'members' or (isinstance(value, list) and path == ''):
                member_ids = []
                items = value if path == 'members' else (value if isinstance(value, list) else [])
                for item in items or []:
                    if isinstance(item, dict) and item.get('value'):
                        try:
                            member_ids.append(uuid.UUID(str(item['value'])))
                        except ValueError:
                            continue
                if member_ids:
                    Membership.objects.filter(
                        organization=scim.organization,
                        user_id__in=member_ids,
                    ).update(department=department)
        log_activity(
            None,
            'admin_action',
            {'action': 'scim_group_updated', 'department_id': str(department.id)},
            organization=scim.organization,
            request=request,
        )
        return Response(_group_to_scim(department), content_type=SCIM_CONTENT_TYPE)

    def delete(self, request, group_id):
        resolved, err = self._resolve(request, group_id)
        if err:
            return err
        scim, department = resolved
        Membership.objects.filter(department=department).update(department=None)
        dept_id = str(department.id)
        department.delete()
        log_activity(
            None,
            'admin_action',
            {'action': 'scim_group_deleted', 'department_id': dept_id},
            organization=scim.organization,
            request=request,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
