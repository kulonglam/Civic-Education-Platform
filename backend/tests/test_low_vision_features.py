import pytest
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status

from apps.engagement.models import Petition, Poll, PollOption
from apps.gamification.models import Badge
from apps.learning.models import Article, MediaAsset
from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org


@pytest.fixture
def free_plan(db):
    from apps.billing.models import Plan

    return Plan.objects.create(
        code='free',
        name='Free',
        price_cents=0,
        sort_order=0,
        features={'tutor_daily_messages': 30},
    )


@pytest.fixture
def badges(org):
    badge, _ = Badge.objects.get_or_create(
        organization=org,
        slug='first_steps',
        defaults={'name': 'First Steps', 'xp_required': 25, 'sort_order': 1},
    )
    return badge


@pytest.fixture
def open_poll(org, citizen_user):
    poll = Poll.objects.create(
        organization=org,
        question='Test poll?',
        status=Poll.STATUS_OPEN,
        created_by=citizen_user,
    )
    PollOption.objects.create(organization=org, poll=poll, label='Yes')
    PollOption.objects.create(organization=org, poll=poll, label='No')
    return poll


@pytest.mark.django_db
class TestGamification:
    def test_gamification_me(self, api_client, org, citizen_user, free_plan, badges):
        from apps.billing.models import Subscription

        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)

        response = api_client.get('/api/gamification/me/')
        assert response.status_code == status.HTTP_200_OK
        assert 'xp_points' in response.data
        assert 'badges_earned' in response.data

    def test_article_complete_awards_xp(self, api_client, org, citizen_user, category, free_plan):
        from apps.billing.models import Subscription

        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)

        article = Article.objects.create(
            organization=org,
            title='XP Article',
            content='Content for XP test.',
            category=category,
            author=citizen_user,
            status='published',
            published_at=timezone.now(),
        )
        api_client.post(f'/api/articles/{article.id}/progress/', {'completed': True}, format='json')

        me = api_client.get('/api/gamification/me/')
        assert me.data['xp_points'] >= 25


@pytest.mark.django_db
class TestEngagement:
    def test_list_polls(self, api_client, org, citizen_user, open_poll, free_plan):
        from apps.billing.models import Subscription

        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)

        response = api_client.get('/api/engagement/polls/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_vote_poll(self, api_client, org, citizen_user, open_poll, free_plan):
        from apps.billing.models import Subscription

        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)

        option_id = open_poll.options.first().id
        response = api_client.post(
            f'/api/engagement/polls/{open_poll.id}/vote/',
            {'option_id': str(option_id)},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user_vote_option_id'] == str(option_id)

    def test_sign_petition(self, api_client, org, citizen_user, free_plan):
        from apps.billing.models import Subscription

        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)

        petition = Petition.objects.create(
            organization=org,
            title='Test petition',
            description='Please sign.',
            status=Petition.STATUS_OPEN,
            created_by=citizen_user,
        )
        response = api_client.post(f'/api/engagement/petitions/{petition.id}/sign/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user_signed'] is True


@pytest.mark.django_db
class TestMediaCaptions:
    def test_captions_url_on_media(self, api_client, org, citizen_user, category, free_plan):
        from apps.billing.models import Subscription

        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.OWNER)

        media = MediaAsset.objects.create(
            organization=org,
            title='Captioned video',
            media_type=MediaAsset.TYPE_VIDEO,
            external_url='https://example.org/video.mp4',
            captions_url='https://example.org/captions.vtt',
            category=category,
            status='published',
            published_at=timezone.now(),
            author=citizen_user,
        )
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get(f'/api/media/{media.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['captions_url'] == 'https://example.org/captions.vtt'


@pytest.mark.django_db
class TestTutorStream:
    def test_stream_endpoint_returns_sse(self, api_client, org, citizen_user, free_plan):
        from apps.billing.models import Subscription

        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)

        response = api_client.post(
            '/api/tutor/chat/stream/',
            {'message': 'What is civic education?'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'].startswith('text/event-stream')
        body = b''.join(response.streaming_content).decode()
        assert 'event: done' in body or 'event: token' in body


@pytest.mark.django_db
class TestTutorIndex:
    def test_article_save_builds_index(self, org, citizen_user, category):
        article = Article.objects.create(
            organization=org,
            title='Indexed',
            content='Short body.',
            category=category,
            author=citizen_user,
            status='published',
        )
        article.refresh_from_db()
        assert 'Short body' in article.tutor_index_text

    def test_invalidate_attachment_cache(self):
        from apps.tutor.document_text import _cache_key, invalidate_attachment_text_cache

        url = 'https://example.org/doc.pdf'
        cache.set(_cache_key(url), 'cached text', timeout=3600)
        invalidate_attachment_text_cache(url)
        assert cache.get(_cache_key(url)) is None
