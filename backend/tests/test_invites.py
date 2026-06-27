import pytest
from django.core import mail
from rest_framework import status

from apps.tenants.models import Membership, OrganizationInvite
from apps.tenants.services import create_organization_with_owner
from tests.conftest import bind_client_to_org


@pytest.mark.django_db
class TestOrganizationInvites:
    def test_invite_unknown_email_sends_pending_invite(self, api_client, org, citizen_user):
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.OWNER)
        response = api_client.post('/api/organization/members/invite/', {
            'email': 'newcolleague@test.com',
            'role': Membership.MEMBER,
        }, format='json')
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert OrganizationInvite.objects.filter(email='newcolleague@test.com', organization=org).exists()
        assert len(mail.outbox) == 1
        assert 'invite/' in mail.outbox[0].body

    def test_invite_existing_user_adds_member_immediately(self, api_client, org, citizen_user, editor_user):
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.OWNER)
        Membership.objects.filter(organization=org, user=editor_user).delete()

        response = api_client.post('/api/organization/members/invite/', {
            'email': editor_user.email,
            'role': Membership.MEMBER,
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Membership.objects.filter(organization=org, user=editor_user).exists()

    def test_register_with_invite_token_joins_org(self, api_client, org, citizen_user, roles):
        from apps.billing.models import Plan

        Plan.objects.get_or_create(code='free', defaults={'name': 'Free', 'price_cents': 0, 'sort_order': 0})
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.OWNER)
        api_client.post('/api/organization/members/invite/', {
            'email': 'invited@test.com',
            'role': Membership.MEMBER,
        }, format='json')
        invite = OrganizationInvite.objects.get(email='invited@test.com')

        api_client.force_authenticate(user=None)
        api_client.credentials()
        response = api_client.post('/api/auth/register/', {
            'email': 'invited@test.com',
            'first_name': 'Invited',
            'last_name': 'User',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'invite_token': invite.token,
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Membership.objects.filter(organization=org, user__email='invited@test.com').exists()
        assert OrganizationInvite.objects.get(id=invite.id).accepted_at is not None

    def test_accept_invite_when_logged_in(self, api_client, org, citizen_user, django_user_model):
        from datetime import timedelta

        from django.utils import timezone

        django_user_model.objects.create_user(
            email='accept@test.com',
            password='TestPass123!',
            first_name='Accept',
            last_name='User',
        )
        invite = OrganizationInvite.objects.create(
            organization=org,
            email='accept@test.com',
            role=Membership.MEMBER,
            token=OrganizationInvite.generate_token(),
            invited_by=citizen_user,
            expires_at=timezone.now() + timedelta(days=7),
        )

        login = api_client.post('/api/auth/login/', {
            'email': 'accept@test.com',
            'password': 'TestPass123!',
        }, format='json')
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}',
            HTTP_X_TENANT_SLUG=org.slug,
        )
        response = api_client.post(f'/api/organization/invites/accept/{invite.token}/')
        assert response.status_code == status.HTTP_201_CREATED
        assert Membership.objects.filter(organization=org, user__email='accept@test.com').exists()

    def test_invite_preview_public(self, api_client, org, citizen_user):
        from django.utils import timezone
        from datetime import timedelta

        invite = OrganizationInvite.objects.create(
            organization=org,
            email='preview@test.com',
            role=Membership.MEMBER,
            token=OrganizationInvite.generate_token(),
            invited_by=citizen_user,
            expires_at=timezone.now() + timedelta(days=7),
        )
        response = api_client.get(f'/api/organization/invites/preview/{invite.token}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['organization']['slug'] == org.slug
        assert response.data['email'] == 'preview@test.com'
