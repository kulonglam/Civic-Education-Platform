"""Grade-A enterprise: sessions, SCIM, compliance, support, IP allowlist."""

import hashlib
import time

import pytest
from django.core.cache import cache
from rest_framework import status

from apps.accounts.models import Role
from apps.accounts.tokens import EmailTokenObtainPairSerializer
from apps.audit.services import log_activity, verify_audit_chain
from apps.tenants.models import Membership, OrganizationScimToken, SupportCase
from tests.conftest import bind_client_to_org, enable_mfa, login_user


def _token_hash(raw: str) -> str:
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


@pytest.mark.django_db
class TestSessionControls:
    def test_password_change_revokes_prior_tokens(
        self, api_client, django_user_model, roles, org
    ):
        user = django_user_model.objects.create_user(
            email='epoch@test.com',
            password='OldPass123!',
            first_name='E',
            last_name='Poch',
        )
        Membership.objects.create(organization=org, user=user, role=Membership.OWNER)
        enable_mfa(user)

        login = login_user(api_client, user, password='OldPass123!')
        assert login.status_code == 200, login.data
        old_access = login.data['access']
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {old_access}',
            HTTP_X_TENANT_SLUG=org.slug,
        )

        response = api_client.post(
            '/api/auth/password/change/',
            {'current_password': 'OldPass123!', 'new_password': 'NewPass123!'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK, response.data

        denied = api_client.get('/api/users/profile/')
        assert denied.status_code == status.HTTP_401_UNAUTHORIZED

    def test_idle_timeout_for_privileged_user(
        self, api_client, django_user_model, roles, org, settings
    ):
        settings.SESSION_IDLE_TIMEOUT_SECONDS = 1
        admin_role = Role.objects.get(name='admin')
        user = django_user_model.objects.create_user(
            email='idle@test.com',
            password='TestPass123!',
            first_name='I',
            last_name='Dle',
            role=admin_role,
            is_staff=True,
        )
        Membership.objects.create(organization=org, user=user, role=Membership.OWNER)
        enable_mfa(user)

        login = login_user(api_client, user)
        assert login.status_code == 200, login.data
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}',
            HTTP_X_TENANT_SLUG=org.slug,
        )

        cache.set(f'session:activity:{user.id}', time.time() - 10, timeout=60)
        response = api_client.get('/api/users/profile/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAuditIntegrity:
    def test_hash_chain_valid(self, citizen_user, org):
        log_activity(citizen_user, 'user_login', {'n': 1}, organization=org)
        log_activity(citizen_user, 'user_logout', {'n': 2}, organization=org)
        result = verify_audit_chain(organization=org)
        assert result['valid'] is True
        assert result['checked'] >= 2


@pytest.mark.django_db
class TestScimProvisioning:
    def test_scim_create_and_deactivate(self, api_client, org, roles):
        raw = 'cep_scim_test_token_abc123xyz'
        OrganizationScimToken.objects.create(
            organization=org,
            name='test',
            token_prefix=raw[:12],
            token_hash=_token_hash(raw),
        )
        create = api_client.post(
            '/scim/v2/Users',
            {
                'schemas': ['urn:ietf:params:scim:schemas:core:2.0:User'],
                'userName': 'scim.user@example.com',
                'name': {'givenName': 'Scim', 'familyName': 'User'},
                'active': True,
            },
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {raw}',
        )
        assert create.status_code in (200, 201), create.data
        user_id = create.data['id']
        assert Membership.objects.filter(
            organization=org, user_id=user_id
        ).exists()

        deactivate = api_client.patch(
            f'/scim/v2/Users/{user_id}',
            {
                'schemas': ['urn:ietf:params:scim:api:messages:2.0:PatchOp'],
                'Operations': [{'op': 'replace', 'path': 'active', 'value': False}],
            },
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {raw}',
        )
        assert deactivate.status_code == 200, deactivate.data
        assert not Membership.objects.filter(
            organization=org, user_id=user_id
        ).exists()

    def test_scim_groups_create(self, api_client, org):
        raw = 'cep_scim_groups_token_xyz'
        OrganizationScimToken.objects.create(
            organization=org,
            name='groups',
            token_prefix=raw[:12],
            token_hash=_token_hash(raw),
        )
        created = api_client.post(
            '/scim/v2/Groups',
            {
                'schemas': ['urn:ietf:params:scim:schemas:core:2.0:Group'],
                'displayName': 'Education Desk',
            },
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {raw}',
        )
        assert created.status_code == 201, created.data
        listed = api_client.get(
            '/scim/v2/Groups',
            HTTP_AUTHORIZATION=f'Bearer {raw}',
        )
        assert listed.status_code == 200
        assert listed.data['totalResults'] >= 1


@pytest.mark.django_db
class TestSupportAndCompliance:
    def test_support_case_and_compliance_pack(
        self, api_client, django_user_model, roles, org
    ):
        owner = django_user_model.objects.create_user(
            email='owner-ga@test.com',
            password='TestPass123!',
            first_name='Own',
            last_name='Er',
        )
        Membership.objects.create(organization=org, user=owner, role=Membership.OWNER)
        enable_mfa(owner)
        bind_client_to_org(api_client, owner, org, membership_role=Membership.OWNER)

        created = api_client.post(
            '/api/organization/support/cases/',
            {
                'subject': 'SSO help',
                'body': 'Need IdP mapping assistance',
                'priority': 'high',
            },
            format='json',
        )
        assert created.status_code == status.HTTP_201_CREATED, created.data
        assert SupportCase.objects.filter(organization=org).count() == 1

        pack = api_client.get('/api/organization/compliance/pack/')
        assert pack.status_code == status.HTTP_200_OK, pack.data
        assert pack.data.get('pack_version') == 2
        assert 'controls' in pack.data
        assert 'control_matrix' in pack.data
        assert len(pack.data['control_matrix']) >= 5
        assert 'integrity' in pack.data

        token = api_client.post(
            '/api/organization/scim/tokens/',
            {'name': 'Azure AD'},
            format='json',
        )
        assert token.status_code == status.HTTP_201_CREATED, token.data
        assert token.data.get('token', '').startswith('cep_scim_')


@pytest.mark.django_db
class TestIpAllowlist:
    def test_blocks_non_allowlisted_ip(
        self, api_client, django_user_model, roles, org
    ):
        org.ip_allowlist = ['203.0.113.10']
        org.save(update_fields=['ip_allowlist'])
        owner = django_user_model.objects.create_user(
            email='ip@test.com',
            password='TestPass123!',
            first_name='Ip',
            last_name='Test',
        )
        Membership.objects.create(organization=org, user=owner, role=Membership.OWNER)
        enable_mfa(owner)
        bind_client_to_org(api_client, owner, org, membership_role=Membership.OWNER)

        response = api_client.get(
            '/api/organization/current/',
            REMOTE_ADDR='198.51.100.1',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json().get('code') == 'ip_not_allowed'
