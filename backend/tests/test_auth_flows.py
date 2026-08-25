import pytest
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status

from apps.accounts.models import EmailVerificationToken


@pytest.mark.django_db
class TestTokenRefresh:
    def test_refresh_returns_new_access_token(self, api_client, citizen_user):
        login = api_client.post('/api/auth/login/', {
            'email': 'citizen@test.com',
            'password': 'TestPass123!',
        })
        refresh = login.data['refresh']

        response = api_client.post('/api/auth/token/refresh/', {'refresh': refresh})
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_refresh_rejects_garbage_token(self, api_client):
        response = api_client.post('/api/auth/token/refresh/', {'refresh': 'not-a-token'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLogoutBlacklist:
    def test_logout_blacklists_refresh_token(self, api_client, citizen_user):
        login = api_client.post('/api/auth/login/', {
            'email': 'citizen@test.com',
            'password': 'TestPass123!',
        })
        refresh = login.data['refresh']

        api_client.force_authenticate(user=citizen_user)
        logout = api_client.post('/api/auth/logout/', {'refresh': refresh})
        assert logout.status_code == status.HTTP_200_OK

        api_client.force_authenticate(user=None)
        reuse = api_client.post('/api/auth/token/refresh/', {'refresh': refresh})
        assert reuse.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestSuspension:
    def test_suspended_user_cannot_login(self, api_client, citizen_user):
        citizen_user.is_suspended = True
        citizen_user.save(update_fields=['is_suspended'])

        response = api_client.post('/api/auth/login/', {
            'email': 'citizen@test.com',
            'password': 'TestPass123!',
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_suspend_user(self, api_client, admin_user, citizen_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(f'/api/users/{citizen_user.id}/suspend/')
        assert response.status_code == status.HTTP_200_OK
        citizen_user.refresh_from_db()
        assert citizen_user.is_suspended is True

    def test_citizen_cannot_suspend_user(self, api_client, citizen_user, editor_user):
        api_client.force_authenticate(user=citizen_user)
        response = api_client.post(f'/api/users/{editor_user.id}/suspend/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestEmailVerification:
    def test_register_queues_verification_email(self, api_client, roles):
        response = api_client.post('/api/auth/register/', {
            'email': 'verify@test.com',
            'first_name': 'Verify',
            'last_name': 'Me',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get('email_sent') is True
        # send_transactional_email uses locmem in tests.
        assert len(mail.outbox) == 1
        assert 'verify@test.com' in mail.outbox[0].to

    def test_verify_email_marks_user_verified(self, api_client, citizen_user):
        from datetime import timedelta

        from django.utils import timezone

        token = EmailVerificationToken.objects.create(
            user=citizen_user,
            token='valid-token-123',
            expires_at=timezone.now() + timedelta(hours=1),
        )
        response = api_client.get(f'/api/auth/verify-email/{token.token}/')
        assert response.status_code == status.HTTP_200_OK
        citizen_user.refresh_from_db()
        assert citizen_user.email_verified is True

    def test_verify_email_rejects_invalid_token(self, api_client, db):
        response = api_client.get('/api/auth/verify-email/nope/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPasswordReset:
    def test_reset_request_sends_email_for_known_user(self, api_client, citizen_user):
        response = api_client.post('/api/auth/password/reset/', {'email': 'citizen@test.com'})
        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1

    def test_reset_request_is_silent_for_unknown_user(self, api_client, db):
        response = api_client.post('/api/auth/password/reset/', {'email': 'ghost@test.com'})
        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 0

    def test_reset_confirm_changes_password(self, api_client, citizen_user):
        uid = urlsafe_base64_encode(force_bytes(citizen_user.pk))
        token = default_token_generator.make_token(citizen_user)
        response = api_client.post('/api/auth/password/reset/confirm/', {
            'uid': uid,
            'token': token,
            'password': 'BrandNewPass456!',
        })
        assert response.status_code == status.HTTP_200_OK

        login = api_client.post('/api/auth/login/', {
            'email': 'citizen@test.com',
            'password': 'BrandNewPass456!',
        })
        assert login.status_code == status.HTTP_200_OK

    def test_reset_confirm_rejects_bad_token(self, api_client, citizen_user):
        uid = urlsafe_base64_encode(force_bytes(citizen_user.pk))
        response = api_client.post('/api/auth/password/reset/confirm/', {
            'uid': uid,
            'token': 'bad-token',
            'password': 'BrandNewPass456!',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
