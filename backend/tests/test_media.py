import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.learning.models import MediaAsset
from apps.learning.serializers import validate_http_url
from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org


@pytest.mark.django_db
class TestMediaHttpUrlValidation:
    def test_rejects_non_http_schemes(self):
        with pytest.raises(ValidationError):
            validate_http_url('file:///etc/passwd', field_name='External URL')

    def test_allows_https(self):
        assert validate_http_url('https://cdn.example.com/a.mp3') == 'https://cdn.example.com/a.mp3'


@pytest.mark.django_db
class TestMediaLibraryApi:
    def test_anonymous_sees_only_published(self, api_client, org, category, editor_user):
        MediaAsset.objects.create(
            organization=org,
            title='Published audio',
            media_type=MediaAsset.TYPE_AUDIO,
            source=MediaAsset.SOURCE_EXTERNAL,
            external_url='https://cdn.example.com/a.mp3',
            category=category,
            status='published',
            published_at=timezone.now(),
            author=editor_user,
        )
        MediaAsset.objects.create(
            organization=org,
            title='Draft audio',
            media_type=MediaAsset.TYPE_AUDIO,
            source=MediaAsset.SOURCE_EXTERNAL,
            external_url='https://cdn.example.com/draft.mp3',
            category=category,
            status='draft',
            author=editor_user,
        )

        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/media/')
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        titles = [item['title'] for item in results]
        assert 'Published audio' in titles
        assert 'Draft audio' not in titles

    def test_editor_can_create_external_video(self, api_client, org, category, editor_user):
        bind_client_to_org(
            api_client,
            editor_user,
            org,
            membership_role=Membership.CONTENT_MANAGER,
        )
        response = api_client.post(
            '/api/media/',
            {
                'title': 'Civic explainer',
                'media_type': 'video',
                'source': 'external',
                'external_url': 'https://www.youtube.com/watch?v=0PAy1zBtT9w',
                'category_id': str(category.id),
                'status': 'published',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['playback_url'].startswith('https://')
        assert MediaAsset.objects.filter(title='Civic explainer').exists()

    def test_audio_upload_rejects_wrong_type(self, api_client, org, editor_user):
        bind_client_to_org(
            api_client,
            editor_user,
            org,
            membership_role=Membership.CONTENT_MANAGER,
        )
        bad = SimpleUploadedFile('notes.txt', b'not audio', content_type='text/plain')
        response = api_client.post(
            '/api/media/audio/upload/',
            {'file': bad},
            format='multipart',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_audio_upload_accepts_mp3(self, api_client, org, editor_user):
        bind_client_to_org(
            api_client,
            editor_user,
            org,
            membership_role=Membership.CONTENT_MANAGER,
        )
        audio = SimpleUploadedFile(
            'lesson.mp3',
            b'ID3fake-mp3-bytes',
            content_type='audio/mpeg',
        )
        response = api_client.post(
            '/api/media/audio/upload/',
            {'file': audio},
            format='multipart',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['source'] == 'upload'
        assert response.data['url']
