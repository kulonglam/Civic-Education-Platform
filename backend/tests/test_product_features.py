import pytest
from rest_framework import status

from apps.accounts.models import PhoneOTP
from apps.audit.models import ActivityLog
from apps.notifications.models import Notification, WebPushSubscription
from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org


@pytest.mark.django_db
class TestResendVerificationEmail:
    def test_resend_queues_email(self, api_client, citizen_user):
        api_client.force_authenticate(user=citizen_user)
        response = api_client.post('/api/auth/verify-email/resend/')
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data

    def test_resend_when_already_verified(self, api_client, citizen_user):
        citizen_user.email_verified = True
        citizen_user.save(update_fields=['email_verified'])
        api_client.force_authenticate(user=citizen_user)
        response = api_client.post('/api/auth/verify-email/resend/')
        assert response.status_code == status.HTTP_200_OK
        assert 'already verified' in response.data['message'].lower()


@pytest.mark.django_db
class TestPhoneVerification:
    def test_send_requires_phone(self, api_client, citizen_user):
        api_client.force_authenticate(user=citizen_user)
        response = api_client.post('/api/auth/phone/verify/send/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_phone_verify_flow(self, api_client, citizen_user, org):
        citizen_user.phone = '+211922333444'
        citizen_user.save(update_fields=['phone'])
        api_client.force_authenticate(user=citizen_user)

        send = api_client.post('/api/auth/phone/verify/send/')
        assert send.status_code == status.HTTP_200_OK

        otp = PhoneOTP.objects.filter(user=citizen_user, used=False).first()
        assert otp is not None

        confirm = api_client.post(
            '/api/auth/phone/verify/confirm/',
            {'code': otp.code},
            format='json',
        )
        assert confirm.status_code == status.HTTP_200_OK
        citizen_user.refresh_from_db()
        assert citizen_user.phone_verified is True


@pytest.mark.django_db
class TestUnsuspendUser:
    def test_moderator_can_unsuspend(self, api_client, moderator_user, citizen_user):
        citizen_user.is_suspended = True
        citizen_user.save(update_fields=['is_suspended'])
        api_client.force_authenticate(user=moderator_user)

        response = api_client.post(f'/api/users/{citizen_user.id}/unsuspend/')
        assert response.status_code == status.HTTP_200_OK
        citizen_user.refresh_from_db()
        assert citizen_user.is_suspended is False
        assert ActivityLog.objects.filter(activity_type='user_unsuspended').exists()

    def test_citizen_cannot_unsuspend(self, api_client, citizen_user, editor_user):
        editor_user.is_suspended = True
        editor_user.save(update_fields=['is_suspended'])
        api_client.force_authenticate(user=citizen_user)

        response = api_client.post(f'/api/users/{editor_user.id}/unsuspend/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestInAppBroadcast:
    def test_org_admin_can_broadcast(self, api_client, org, citizen_user, django_user_model):
        member = django_user_model.objects.create_user(
            email='member@announce.test',
            password='TestPass123!',
            first_name='Ann',
            last_name='Member',
        )
        Membership.objects.create(organization=org, user=member, role=Membership.MEMBER)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.OWNER)

        response = api_client.post(
            '/api/notifications/broadcast/',
            {
                'title': 'School closed',
                'message': 'Classes resume Monday.',
                'notification_type': 'announcement',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert Notification.objects.filter(user=member, title='School closed').exists()

    def test_member_cannot_broadcast(self, api_client, org, citizen_user, django_user_model):
        member = django_user_model.objects.create_user(
            email='plain@announce.test',
            password='TestPass123!',
            first_name='Plain',
            last_name='Member',
        )
        Membership.objects.create(organization=org, user=member, role=Membership.MEMBER)
        bind_client_to_org(api_client, member, org)

        response = api_client.post(
            '/api/notifications/broadcast/',
            {'title': 'Nope', 'message': 'Should fail'},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAuditLogs:
    def test_moderator_can_list_logs(self, api_client, moderator_user, citizen_user, org):
        ActivityLog.objects.create(
            organization=org,
            user=citizen_user,
            activity_type='user_login',
            metadata={'ip': '127.0.0.1'},
        )
        bind_client_to_org(api_client, moderator_user, org, membership_role=Membership.ADMIN)

        response = api_client.get('/api/audit/logs/')
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) >= 1

    def test_citizen_cannot_list_logs(self, api_client, citizen_user):
        api_client.force_authenticate(user=citizen_user)
        response = api_client.get('/api/audit/logs/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestWebPushSubscribe:
    def test_subscribe_and_unsubscribe(self, api_client, citizen_user):
        api_client.force_authenticate(user=citizen_user)
        payload = {
            'endpoint': 'https://push.example.test/subscription/1',
            'keys': {'p256dh': 'key1', 'auth': 'auth1'},
        }

        create = api_client.post('/api/notifications/push/subscribe/', payload, format='json')
        assert create.status_code == status.HTTP_201_CREATED
        assert WebPushSubscription.objects.filter(user=citizen_user).exists()

        remove = api_client.delete('/api/notifications/push/subscribe/', payload, format='json')
        assert remove.status_code == status.HTTP_200_OK
        assert not WebPushSubscription.objects.filter(user=citizen_user).exists()
