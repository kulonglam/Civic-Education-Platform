import pytest
from rest_framework import status

from apps.billing.models import Plan, Subscription
from apps.tenants.models import Membership
from apps.tutor.models import TutorChat
from tests.conftest import bind_client_to_org


@pytest.fixture
def free_plan(db):
    return Plan.objects.create(
        code='free',
        name='Free',
        price_cents=0,
        sort_order=0,
        features={'tutor_daily_messages': 30},
    )


@pytest.mark.django_db
class TestTutorChat:
    def test_chat_requires_auth(self, api_client, org):
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.post('/api/tutor/chat/', {'message': 'What are my rights?'}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_chat_returns_reply(self, api_client, org, citizen_user, free_plan):
        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.OWNER)

        response = api_client.post(
            '/api/tutor/chat/',
            {'message': 'What is civic education?'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'reply' in response.data
        assert 'sources' in response.data
        assert isinstance(response.data['sources'], list)
        assert response.data['messages_used_today'] == 1
        assert response.data['daily_limit'] == 30

    def test_daily_limit_enforced(self, api_client, org, citizen_user, free_plan, settings):
        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.OWNER)

        from apps.tutor.services import increment_daily_usage

        for _ in range(30):
            increment_daily_usage(citizen_user)

        response = api_client.post(
            '/api/tutor/chat/',
            {'message': 'One more question'},
            format='json',
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_clear_session(self, api_client, org, citizen_user, free_plan):
        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.OWNER)

        api_client.post('/api/tutor/chat/', {'message': 'Hello'}, format='json')
        response = api_client.delete('/api/tutor/chat/session/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

        usage = api_client.get('/api/tutor/usage/')
        assert usage.status_code == status.HTTP_200_OK
        assert usage.data['session_message_count'] == 0

    def test_usage_endpoint(self, api_client, org, citizen_user, free_plan):
        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.OWNER)

        response = api_client.get('/api/tutor/usage/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['daily_limit'] == 30
        assert response.data['messages_used_today'] == 0

    def test_persists_chat_via_task(self, api_client, org, citizen_user, free_plan):
        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.OWNER)

        api_client.post('/api/tutor/chat/', {'message': 'Explain elections'}, format='json')
        assert TutorChat.objects.filter(user=citizen_user).count() == 2


@pytest.mark.django_db
class TestTutorAdminUsage:
    def test_platform_usage_requires_admin(self, api_client, org, citizen_user, free_plan):
        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)

        response = api_client.get('/api/tutor/usage/platform/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_platform_usage_returns_aggregate(self, api_client, org, admin_user, citizen_user, free_plan):
        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)

        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)
        api_client.post('/api/tutor/chat/', {'message': 'Hello'}, format='json')

        bind_client_to_org(api_client, admin_user, org, membership_role=Membership.OWNER)
        response = api_client.get('/api/tutor/usage/platform/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['messages_today'] >= 1
        assert 'tokens_today' in response.data
        assert 'active_users_today' in response.data


@pytest.mark.django_db
class TestTutorPromptVoice:
    def test_system_prompt_forbids_report_tables(self, org, citizen_user):
        from apps.tenants.context import set_current_organization
        from apps.tutor.prompts import build_system_prompt

        set_current_organization(org)
        prompt = build_system_prompt(citizen_user, None, 'What are the takeaways?')
        assert 'markdown tables' in prompt
        assert 'Key Take-aways' in prompt
        assert '220 words' in prompt
