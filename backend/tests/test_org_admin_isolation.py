"""Org admins must not read another organization's data."""

import pytest
from rest_framework import status

from apps.accounts.models import Role
from apps.learning.models import Article, Category
from apps.tenants.models import Membership
from apps.tenants.services import create_organization_with_owner
from tests.conftest import bind_client_to_org, enable_mfa, login_user


def _editor_owner(django_user_model, email):
    role = Role.objects.get(name='editor')
    return django_user_model.objects.create_user(
        email=email,
        password='TestPass123!',
        first_name='Org',
        last_name='Admin',
        role=role,
    )


@pytest.mark.django_db
class TestOrgAdminIsolation:
    def test_cannot_spoof_header_to_list_foreign_articles(
        self, api_client, django_user_model, roles
    ):
        owner_a = _editor_owner(django_user_model, 'owner-a@test.com')
        owner_b = _editor_owner(django_user_model, 'owner-b@test.com')
        org_a = create_organization_with_owner(name='Org A', owner=owner_a, slug='org-a')
        org_b = create_organization_with_owner(name='Org B', owner=owner_b, slug='org-b')
        cat_a = Category.objects.create(organization=org_a, name='Ours', slug='ours')
        cat_b = Category.objects.create(organization=org_b, name='Theirs', slug='theirs')
        Article.all_objects.create(
            organization=org_a,
            title='Public in home org',
            content='Body',
            category=cat_a,
            status='published',
        )
        Article.all_objects.create(
            organization=org_b,
            title='Secret lesson',
            content='Must not leak',
            category=cat_b,
            status='published',
        )

        enable_mfa(owner_a)
        login = login_user(api_client, owner_a)
        assert login.status_code == status.HTTP_200_OK
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}',
            HTTP_X_TENANT_SLUG=org_b.slug,
        )
        response = api_client.get('/api/articles/')
        assert response.status_code == status.HTTP_200_OK
        titles = [row['title'] for row in response.data['results']]
        assert 'Secret lesson' not in titles
        assert 'Public in home org' in titles

    def test_cannot_list_foreign_org_members(self, api_client, django_user_model, roles):
        owner_a = _editor_owner(django_user_model, 'members-a@test.com')
        owner_b = _editor_owner(django_user_model, 'members-b@test.com')
        org_a = create_organization_with_owner(name='Members A', owner=owner_a, slug='members-a')
        org_b = create_organization_with_owner(name='Members B', owner=owner_b, slug='members-b')

        enable_mfa(owner_a)
        login = login_user(api_client, owner_a)
        assert login.status_code == status.HTTP_200_OK
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}',
            HTTP_X_TENANT_SLUG=org_b.slug,
        )
        response = api_client.get('/api/organization/members/')
        assert response.status_code == status.HTTP_200_OK
        emails = [row['user_email'] for row in response.data['results']]
        assert owner_b.email not in emails
        assert owner_a.email in emails

    def test_cannot_read_platform_usage_or_overview(
        self, api_client, org, citizen_user
    ):
        bind_client_to_org(
            api_client,
            citizen_user,
            org,
            membership_role=Membership.OWNER,
        )
        usage = api_client.get('/api/organization/platform/usage/')
        assert usage.status_code == status.HTTP_403_FORBIDDEN
        overview = api_client.get('/api/analytics/overview/')
        assert overview.status_code == status.HTTP_403_FORBIDDEN

    def test_moderator_user_list_without_tenant_is_empty(
        self, api_client, moderator_user
    ):
        api_client.force_authenticate(user=moderator_user)
        response = api_client.get('/api/users/')
        assert response.status_code == status.HTTP_200_OK
        rows = response.data['results'] if isinstance(response.data, dict) else response.data
        assert rows == []
