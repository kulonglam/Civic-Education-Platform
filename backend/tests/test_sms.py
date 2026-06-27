import pytest
from rest_framework import status

from apps.billing.models import Plan, Subscription
from apps.notifications.models import SmsMessage
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


@pytest.fixture
def free_plan(db):
    return Plan.objects.create(
        code='free',
        name='Free',
        price_cents=0,
        sort_order=0,
        features={'sms_alerts': False},
    )


@pytest.mark.django_db
class TestSmsAlerts:
    def test_send_sms_requires_paid_plan(self, api_client, org, citizen_user, free_plan):
        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.OWNER)

        response = api_client.post(
            '/api/notify/sms/',
            {'message': 'Hello', 'phones': ['+211922123456']},
            format='json',
        )
        assert response.status_code == status.HTTP_402_PAYMENT_REQUIRED

    def test_send_sms_queues_message(self, api_client, org, citizen_user, pro_plan, django_user_model):
        Subscription.objects.create(organization=org, plan=pro_plan, status=Subscription.ACTIVE)
        member = django_user_model.objects.create_user(
            email='member@sms.test',
            password='TestPass123!',
            first_name='SMS',
            last_name='Member',
            phone='+211922123456',
        )
        Membership.objects.create(organization=org, user=member, role=Membership.MEMBER)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.OWNER)

        response = api_client.post(
            '/api/notify/sms/',
            {'message': 'School alert', 'user_ids': [str(member.id)]},
            format='json',
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert SmsMessage.all_objects.filter(organization=org, phone='+211922123456').exists()

    def test_broadcast_sms(self, api_client, org, citizen_user, pro_plan):
        Subscription.objects.create(organization=org, plan=pro_plan, status=Subscription.ACTIVE)
        citizen_user.phone = '+211922999888'
        citizen_user.save(update_fields=['phone'])
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.OWNER)

        response = api_client.post(
            '/api/notify/broadcast/',
            {'message': 'Civic alert for all members'},
            format='json',
        )
        assert response.status_code == status.HTTP_202_ACCEPTED

    def test_sms_history(self, api_client, org, citizen_user, pro_plan):
        Subscription.objects.create(organization=org, plan=pro_plan, status=Subscription.ACTIVE)
        SmsMessage.all_objects.create(
            organization=org,
            user=citizen_user,
            phone='+211922123456',
            message='Test',
            message_type=SmsMessage.TYPE_SMS,
            status=SmsMessage.STATUS_SENT,
        )
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.OWNER)

        response = api_client.get('/api/notify/history/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1


@pytest.mark.django_db
class TestPhoneOtp:
    def test_password_reset_otp_flow(self, api_client, citizen_user, org):
        citizen_user.phone = '+211922111222'
        citizen_user.save(update_fields=['phone'])

        request = api_client.post(
            '/api/auth/password/reset/otp/',
            {'phone': '+211922111222'},
            format='json',
        )
        assert request.status_code == status.HTTP_200_OK

        from apps.accounts.models import PhoneOTP

        otp = PhoneOTP.objects.filter(user=citizen_user, used=False).first()
        assert otp is not None

        confirm = api_client.post(
            '/api/auth/password/reset/otp/confirm/',
            {'phone': '+211922111222', 'code': otp.code, 'password': 'NewSecurePass1!'},
            format='json',
        )
        assert confirm.status_code == status.HTTP_200_OK
        citizen_user.refresh_from_db()
        assert citizen_user.check_password('NewSecurePass1!')
