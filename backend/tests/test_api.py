import pytest
from rest_framework import status

from apps.learning.models import Article, Category
from tests.conftest import bind_client_to_org


@pytest.fixture
def category(db, org):
    return Category.objects.create(organization=org, name='Constitution', slug='constitution')


@pytest.mark.django_db
class TestHealthCheck:
    def test_health_endpoint(self, api_client):
        response = api_client.get('/api/health/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'ok'


@pytest.mark.django_db
class TestAuth:
    def test_register(self, api_client, roles):
        from apps.billing.models import Plan

        Plan.objects.get_or_create(code='free', defaults={'name': 'Free', 'price_cents': 0, 'sort_order': 0})
        response = api_client.post('/api/auth/register/', {
            'email': 'newuser@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
        })
        assert response.status_code == status.HTTP_201_CREATED

    def test_login(self, api_client, citizen_user):
        response = api_client.post('/api/auth/login/', {
            'email': 'citizen@test.com',
            'password': 'TestPass123!',
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_profile_requires_auth(self, api_client):
        response = api_client.get('/api/users/profile/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestArticles:
    def test_list_published_articles_public(self, api_client, category, editor_user, org):
        bind_client_to_org(api_client, editor_user, org)
        Article.objects.create(
            title='Test Article',
            content='Content here',
            category=category,
            author=editor_user,
            organization=org,
            status='published',
        )
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        api_client.force_authenticate(user=None)
        response = api_client.get('/api/articles/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_create_article_requires_editor(self, api_client, citizen_user, category, org):
        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.post('/api/articles/', {
            'title': 'New Article',
            'content': 'Body',
            'category_id': str(category.id),
            'status': 'draft',
        }, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_article_as_editor(self, api_client, editor_user, category, org):
        bind_client_to_org(api_client, editor_user, org)
        response = api_client.post('/api/articles/', {
            'title': 'Editor Article',
            'content': 'Body text',
            'category_id': str(category.id),
            'status': 'draft',
            'tags': ['civic'],
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED, response.data

    def test_upload_article_attachment(self, api_client, editor_user, org):
        bind_client_to_org(api_client, editor_user, org)
        from django.core.files.uploadedfile import SimpleUploadedFile

        pdf = SimpleUploadedFile(
            'constitution.pdf',
            b'%PDF-1.4 civic education test',
            content_type='application/pdf',
        )
        response = api_client.post(
            '/api/articles/attachments/upload/',
            {'file': pdf},
            format='multipart',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['attachment_url']
        assert response.data['attachment_name'] == 'constitution.pdf'

    def test_create_article_with_attachment(self, api_client, editor_user, category, org):
        bind_client_to_org(api_client, editor_user, org)
        from django.core.files.uploadedfile import SimpleUploadedFile

        pdf = SimpleUploadedFile(
            'constitution.pdf',
            b'%PDF-1.4 civic education test',
            content_type='application/pdf',
        )
        upload = api_client.post(
            '/api/articles/attachments/upload/',
            {'file': pdf},
            format='multipart',
        )
        response = api_client.post('/api/articles/', {
            'title': 'Transitional Constitution',
            'content': 'Summary and link to the full document below.',
            'category_id': str(category.id),
            'tags': ['constitution'],
            'attachment_url': upload.data['attachment_url'],
            'attachment_name': upload.data['attachment_name'],
            'status': 'published',
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED, response.data
        assert response.data['attachment_url'] == upload.data['attachment_url']
