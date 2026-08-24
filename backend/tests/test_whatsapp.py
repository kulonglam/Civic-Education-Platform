import pytest
from rest_framework import status

from apps.billing.models import Plan, Subscription
from apps.notifications.models import WhatsAppMessage
from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org


@pytest.fixture
def pro_plan(db):
    return Plan.objects.create(
        code='pro',
        name='Pro',
        price_cents=2900,
        sort_order=1,
        features={'sms_alerts': True},
    )


@pytest.mark.django_db
class TestWhatsAppChannel:
    def test_status_is_public(self, api_client, org):
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/notify/whatsapp/status/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['share_enabled'] is True
        assert response.data['cloud_configured'] is False

    def test_send_requires_paid_plan(self, api_client, org, citizen_user, db):
        free_plan = Plan.objects.create(
            code='free',
            name='Free',
            price_cents=0,
            features={'sms_alerts': False},
        )
        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.OWNER)
        response = api_client.post(
            '/api/notify/whatsapp/',
            {'message': 'Hello', 'phones': ['+211922123456']},
            format='json',
        )
        assert response.status_code == status.HTTP_402_PAYMENT_REQUIRED

    def test_send_queues_message(self, api_client, org, citizen_user, pro_plan):
        Subscription.objects.create(organization=org, plan=pro_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.OWNER)
        response = api_client.post(
            '/api/notify/whatsapp/',
            {'message': 'Civic alert', 'phones': ['+211922123456']},
            format='json',
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert WhatsAppMessage.all_objects.filter(organization=org, phone='+211922123456').exists()

    def test_webhook_verify_rejects_bad_token(self, api_client, settings):
        settings.WHATSAPP_VERIFY_TOKEN = 'secret-token'
        response = api_client.get(
            '/api/notify/whatsapp/webhook/',
            {'hub.mode': 'subscribe', 'hub.verify_token': 'wrong', 'hub.challenge': '123'},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_webhook_verify_returns_challenge(self, api_client, settings):
        settings.WHATSAPP_VERIFY_TOKEN = 'secret-token'
        response = api_client.get(
            '/api/notify/whatsapp/webhook/',
            {'hub.mode': 'subscribe', 'hub.verify_token': 'secret-token', 'hub.challenge': 'abc'},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.content.decode() == 'abc'
