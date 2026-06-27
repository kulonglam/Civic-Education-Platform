import pyotp
import pytest
from rest_framework import status

from tests.conftest import MFA_TEST_SECRET, bind_client_to_org, enable_mfa


@pytest.mark.django_db
class TestMarkdownXss:
    def test_rejects_script_in_article_content(self, api_client, editor_user, category, org):
        bind_client_to_org(api_client, editor_user, org)
        response = api_client.post('/api/articles/', {
            'title': 'Bad Article',
            'content': 'Hello <script>alert(1)</script>',
            'category_id': str(category.id),
            'status': 'draft',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestMfaLogin:
    def test_admin_with_mfa_gets_challenge(self, api_client, admin_user):
        enable_mfa(admin_user)
        response = api_client.post('/api/auth/login/', {
            'email': admin_user.email,
            'password': 'TestPass123!',
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.data['mfa_required'] is True
        assert 'mfa_token' in response.data
        assert 'access' not in response.data

    def test_mfa_verify_issues_tokens(self, api_client, admin_user):
        enable_mfa(admin_user)
        login = api_client.post('/api/auth/login/', {
            'email': admin_user.email,
            'password': 'TestPass123!',
        })
        totp = pyotp.TOTP(MFA_TEST_SECRET)
        verify = api_client.post('/api/auth/mfa/verify/', {
            'mfa_token': login.data['mfa_token'],
            'code': totp.now(),
        })
        assert verify.status_code == status.HTTP_200_OK
        assert 'access' in verify.data
        assert 'refresh' in verify.data

    def test_admin_without_mfa_gets_setup_flag(self, api_client, admin_user):
        profile = admin_user.profile
        profile.mfa_enabled = False
        profile.totp_secret = ''
        profile.save(update_fields=['mfa_enabled', 'totp_secret'])

        response = api_client.post('/api/auth/login/', {
            'email': admin_user.email,
            'password': 'TestPass123!',
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('mfa_setup_required') is True


@pytest.mark.django_db
class TestMfaEnforcement:
    def test_privileged_route_blocks_without_mfa(self, api_client, admin_user, org):
        profile = admin_user.profile
        profile.mfa_enabled = False
        profile.totp_secret = ''
        profile.save(update_fields=['mfa_enabled', 'totp_secret'])
        bind_client_to_org(api_client, admin_user, org, skip_mfa=True)

        response = api_client.patch(
            f'/api/users/{admin_user.id}/role/',
            {'role': 'editor'},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
