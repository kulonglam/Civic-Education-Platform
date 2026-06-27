import pytest
from rest_framework import status

from apps.notifications.models import Notification


@pytest.fixture
def notifications(db, citizen_user, org):
    return [
        Notification.objects.create(
            user=citizen_user,
            organization=org,
            notification_type='announcement',
            title=f'Notice {i}',
            message='Body',
        )
        for i in range(3)
    ]


@pytest.mark.django_db
class TestNotifications:
    def test_list_requires_auth(self, api_client):
        response = api_client.get('/api/notifications/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_returns_own_notifications(self, api_client, citizen_user, notifications):
        api_client.force_authenticate(user=citizen_user)
        response = api_client.get('/api/notifications/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3

    def test_user_only_sees_own_notifications(self, api_client, editor_user, notifications):
        api_client.force_authenticate(user=editor_user)
        response = api_client.get('/api/notifications/')
        assert response.data['count'] == 0

    def test_mark_single_read(self, api_client, citizen_user, notifications):
        api_client.force_authenticate(user=citizen_user)
        target = notifications[0]
        response = api_client.patch(f'/api/notifications/{target.id}/read/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_read'] is True
        target.refresh_from_db()
        assert target.is_read is True

    def test_mark_all_read(self, api_client, citizen_user, notifications):
        api_client.force_authenticate(user=citizen_user)
        response = api_client.patch('/api/notifications/read-all/')
        assert response.status_code == status.HTTP_200_OK
        assert Notification.objects.filter(user=citizen_user, is_read=False).count() == 0

    def test_filter_unread(self, api_client, citizen_user, notifications):
        notifications[0].is_read = True
        notifications[0].save(update_fields=['is_read'])
        api_client.force_authenticate(user=citizen_user)
        response = api_client.get('/api/notifications/?is_read=false')
        assert response.data['count'] == 2
