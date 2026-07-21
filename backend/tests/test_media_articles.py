"""Coverage-oriented tests for media–article linking and MediaAsset helpers."""

import pytest
from django.utils import timezone
from rest_framework import status

from apps.learning.models import Article, MediaAsset
from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org


@pytest.mark.django_db
def test_media_asset_playback_url_prefers_upload():
    asset = MediaAsset(
        title='Lesson',
        media_type=MediaAsset.TYPE_AUDIO,
        source=MediaAsset.SOURCE_UPLOAD,
        file_url='https://cdn.example.com/a.mp3',
        external_url='https://cdn.example.com/other.mp3',
    )
    assert asset.playback_url == 'https://cdn.example.com/a.mp3'


@pytest.mark.django_db
def test_media_asset_playback_url_external():
    asset = MediaAsset(
        title='Lesson',
        media_type=MediaAsset.TYPE_VIDEO,
        source=MediaAsset.SOURCE_EXTERNAL,
        external_url='https://www.youtube.com/watch?v=abc123',
    )
    assert asset.playback_url.startswith('https://')


@pytest.mark.django_db
def test_article_can_attach_audio_and_video(api_client, org, category, editor_user):
    bind_client_to_org(
        api_client,
        editor_user,
        org,
        membership_role=Membership.CONTENT_MANAGER,
    )
    audio = MediaAsset.objects.create(
        organization=org,
        title='Audio lesson',
        media_type=MediaAsset.TYPE_AUDIO,
        source=MediaAsset.SOURCE_EXTERNAL,
        external_url='https://cdn.example.com/a.mp3',
        status='published',
        published_at=timezone.now(),
        author=editor_user,
        category=category,
    )
    video = MediaAsset.objects.create(
        organization=org,
        title='Video lesson',
        media_type=MediaAsset.TYPE_VIDEO,
        source=MediaAsset.SOURCE_EXTERNAL,
        external_url='https://www.youtube.com/watch?v=0PAy1zBtT9w',
        status='published',
        published_at=timezone.now(),
        author=editor_user,
        category=category,
    )
    response = api_client.post(
        '/api/articles/',
        {
            'title': 'Lesson with media',
            'content': 'Body with linked audio and video.',
            'category_id': str(category.id),
            'audio_media_id': str(audio.id),
            'video_media_id': str(video.id),
            'status': 'draft',
        },
        format='json',
    )
    assert response.status_code == status.HTTP_201_CREATED, response.data
    assert response.data['audio_media']['id'] == str(audio.id)
    assert response.data['video_media']['id'] == str(video.id)

    article = Article.objects.get(id=response.data['id'])
    assert article.audio_media_id == audio.id
    assert article.video_media_id == video.id


@pytest.mark.django_db
def test_article_rejects_wrong_media_type(api_client, org, category, editor_user):
    bind_client_to_org(
        api_client,
        editor_user,
        org,
        membership_role=Membership.CONTENT_MANAGER,
    )
    video = MediaAsset.objects.create(
        organization=org,
        title='Video only',
        media_type=MediaAsset.TYPE_VIDEO,
        source=MediaAsset.SOURCE_EXTERNAL,
        external_url='https://cdn.example.com/v.mp4',
        status='published',
        published_at=timezone.now(),
        author=editor_user,
    )
    response = api_client.post(
        '/api/articles/',
        {
            'title': 'Bad link',
            'content': 'Body',
            'category_id': str(category.id),
            'audio_media_id': str(video.id),
            'status': 'draft',
        },
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
