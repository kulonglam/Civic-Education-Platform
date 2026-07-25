import pytest
from django.utils import timezone
from rest_framework import status

from apps.forum.models import DiscussionTopic
from apps.learning.models import Article, MediaAsset
from apps.tenants.models import Membership
from apps.tutor.models import TutorChat
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


@pytest.mark.django_db
class TestTutorHistory:
    def test_get_active_session(self, api_client, org, citizen_user, free_plan):
        from apps.billing.models import Subscription

        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)

        api_client.post('/api/tutor/chat/', {'message': 'Hello tutor'}, format='json')
        response = api_client.get('/api/tutor/chat/session/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['messages']) == 2

    def test_list_and_load_history(self, api_client, org, citizen_user, free_plan):
        from apps.billing.models import Subscription

        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)

        api_client.post('/api/tutor/chat/', {'message': 'Explain elections'}, format='json')
        session_id = TutorChat.objects.filter(user=citizen_user, role=TutorChat.ROLE_USER).first().session_id

        listing = api_client.get('/api/tutor/chat/history/')
        assert listing.status_code == status.HTTP_200_OK
        assert len(listing.data) >= 1
        assert listing.data[0]['session_id'] == session_id

        detail = api_client.get(f'/api/tutor/chat/history/{session_id}/')
        assert detail.status_code == status.HTTP_200_OK
        assert len(detail.data['messages']) == 2
        assert detail.data['messages'][0]['role'] == 'user'


@pytest.mark.django_db
class TestGlobalSearch:
    def test_search_requires_min_length(self, api_client, org):
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/search/', {'q': 'a'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['articles'] == []

    def test_search_finds_published_content(self, api_client, org, category, citizen_user):
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        Article.objects.create(
            organization=org,
            title='Elections in South Sudan',
            content='How citizens vote and participate in elections.',
            category=category,
            author=citizen_user,
            status='published',
            published_at=timezone.now(),
        )
        MediaAsset.objects.create(
            organization=org,
            title='Peacebuilding podcast',
            description='Community dialogue for reconciliation.',
            media_type=MediaAsset.TYPE_AUDIO,
            source=MediaAsset.SOURCE_EXTERNAL,
            external_url='https://example.com/audio.mp3',
            category=category,
            author=citizen_user,
            status='published',
            published_at=timezone.now(),
        )
        DiscussionTopic.objects.create(
            organization=org,
            title='Forum on governance reform',
            content='Discuss local governance structures.',
            author=citizen_user,
            is_approved=True,
        )

        response = api_client.get('/api/search/', {'q': 'elections'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['articles']) == 1
        assert 'Elections' in response.data['articles'][0]['title']

        media = api_client.get('/api/search/', {'q': 'peacebuilding'})
        assert media.status_code == status.HTTP_200_OK
        assert len(media.data['media']) == 1

        forum = api_client.get('/api/search/', {'q': 'governance'})
        assert forum.status_code == status.HTTP_200_OK
        assert len(forum.data['topics']) == 1
