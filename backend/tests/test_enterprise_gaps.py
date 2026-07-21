"""Tests for remaining enterprise gaps: org RBAC, content packs, platform support."""

import pytest
from rest_framework import status

from apps.core.models import SecurityEvent
from apps.core.security import log_security_event
from apps.learning.models import Category
from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org, enable_mfa


@pytest.mark.django_db
class TestOrgRoleRBAC:
    def test_content_manager_can_create_article(
        self, api_client, citizen_user, category, org, roles
    ):
        bind_client_to_org(
            api_client,
            citizen_user,
            org,
            membership_role=Membership.CONTENT_MANAGER,
            skip_mfa=True,
        )
        response = api_client.post(
            '/api/articles/',
            {
                'title': 'CM Article',
                'content': 'Body',
                'category_id': str(category.id),
                'status': 'draft',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED, response.data

    def test_org_moderator_can_list_pending_forum(
        self, api_client, citizen_user, org, roles
    ):
        bind_client_to_org(
            api_client,
            citizen_user,
            org,
            membership_role=Membership.MODERATOR,
            skip_mfa=True,
        )
        response = api_client.get('/api/topics/pending/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestContentPacks:
    def test_locked_category_cannot_be_deleted(
        self, api_client, django_user_model, roles, org
    ):
        owner = django_user_model.objects.create_user(
            email='cat-owner@test.com',
            password='TestPass123!',
            first_name='Cat',
            last_name='Owner',
        )
        Membership.objects.create(
            organization=org, user=owner, role=Membership.OWNER
        )
        enable_mfa(owner)
        bind_client_to_org(api_client, owner, org, membership_role=Membership.OWNER)
        created = api_client.post(
            '/api/categories/',
            {
                'name': 'Official Curriculum',
                'slug': 'official-curriculum',
                'is_locked': True,
            },
            format='json',
        )
        assert created.status_code == status.HTTP_201_CREATED, created.data
        cat_id = created.data['id']
        response = api_client.delete(f'/api/categories/{cat_id}/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.data
        assert Category.objects.filter(id=cat_id).exists()

    def test_controlled_document_requires_version(
        self, api_client, editor_user, category, org
    ):
        bind_client_to_org(api_client, editor_user, org)
        response = api_client.post(
            '/api/articles/',
            {
                'title': 'Constitution',
                'content': 'Summary',
                'category_id': str(category.id),
                'is_controlled_document': True,
                'status': 'draft',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPlatformSupportAndSecurity:
    def test_platform_usage_and_support_view(self, api_client, admin_user, org):
        bind_client_to_org(api_client, admin_user, org)
        usage = api_client.get('/api/organization/platform/usage/')
        assert usage.status_code == status.HTTP_200_OK
        assert 'totals' in usage.data
        detail = api_client.get(f'/api/organization/platform/orgs/{org.id}/')
        assert detail.status_code == status.HTTP_200_OK
        assert detail.data['slug'] == org.slug
        assert 'member_count' in detail.data

    def test_security_events_persist_and_list(self, api_client, admin_user, org):
        bind_client_to_org(api_client, admin_user, org)
        log_security_event('login_failed', user=admin_user, detail={'reason': 'bad_password'})
        assert SecurityEvent.objects.filter(event_type='login_failed').exists()
        response = api_client.get('/api/security/events/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1
