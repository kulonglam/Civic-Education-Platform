import pytest
from django.test import override_settings
from rest_framework import status

from apps.billing.models import Plan, Subscription
from tests.conftest import bind_client_to_org


@pytest.mark.django_db
class TestSsoStatus:
    @override_settings(OIDC_ISSUER='', OIDC_CLIENT_ID='', OIDC_CLIENT_SECRET='')
    def test_status_reports_not_configured(self, api_client, org):
        plan, _ = Plan.objects.get_or_create(
            code='enterprise',
            defaults={'name': 'Enterprise', 'features': {'sso': True}},
        )
        Subscription.objects.update_or_create(
            organization=org,
            defaults={'plan': plan, 'status': Subscription.ACTIVE},
        )
        response = api_client.get('/api/auth/sso/status/', {'org': org.slug})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['configured'] is False
        assert response.data['enabled_for_org'] is True

    @override_settings(
        OIDC_ISSUER='https://idp.example.com',
        OIDC_CLIENT_ID='client',
        OIDC_CLIENT_SECRET='secret',
    )
    def test_status_includes_login_path_for_enterprise_org(self, api_client, org):
        plan, _ = Plan.objects.get_or_create(
            code='enterprise',
            defaults={'name': 'Enterprise', 'features': {'sso': True}},
        )
        Subscription.objects.update_or_create(
            organization=org,
            defaults={'plan': plan, 'status': Subscription.ACTIVE},
        )
        response = api_client.get('/api/auth/sso/status/', {'org': org.slug})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['configured'] is True
        assert response.data['login_path'] == f'/api/auth/sso/login/?org={org.slug}'

    @override_settings(
        OIDC_ISSUER='https://idp.example.com',
        OIDC_CLIENT_ID='client',
        OIDC_CLIENT_SECRET='secret',
    )
    def test_login_requires_enterprise_plan(self, api_client, org, citizen_user):
        free, _ = Plan.objects.get_or_create(code='free', defaults={'name': 'Free', 'features': {}})
        Subscription.objects.update_or_create(
            organization=org,
            defaults={'plan': free, 'status': Subscription.ACTIVE},
        )
        response = api_client.get('/api/auth/sso/login/', {'org': org.slug})
        assert response.status_code == status.HTTP_402_PAYMENT_REQUIRED


@pytest.mark.django_db
class TestPushAdmin:
    def test_push_stats_requires_platform_admin(self, api_client, citizen_user, org):
        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.get('/api/notifications/push/stats/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_push_stats_for_platform_admin(self, api_client, admin_user):
        from apps.notifications.models import WebPushSubscription

        api_client.force_authenticate(user=admin_user)
        WebPushSubscription.objects.create(
            user=admin_user,
            endpoint='https://push.example/1',
            p256dh='key',
            auth='auth',
        )
        response = api_client.get('/api/notifications/push/stats/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_subscriptions'] == 1

    def test_push_cleanup_removes_inactive_user_subscriptions(
        self, api_client, admin_user, django_user_model
    ):
        from apps.notifications.models import WebPushSubscription

        inactive = django_user_model.objects.create_user(
            email='inactive@test.com',
            password='TestPass123!',
            is_active=False,
        )
        WebPushSubscription.objects.create(
            user=inactive,
            endpoint='https://push.example/inactive',
            p256dh='key',
            auth='auth',
        )
        api_client.force_authenticate(user=admin_user)
        response = api_client.post('/api/notifications/push/cleanup/')
        assert response.status_code == status.HTTP_200_OK
        assert WebPushSubscription.objects.filter(user=inactive).count() == 0
