import pytest
from rest_framework import status

from apps.forum.models import DiscussionComment, DiscussionTopic
from tests.conftest import bind_client_to_org


@pytest.fixture
def topic(db, citizen_user, org):
    return DiscussionTopic.objects.create(
        title='Civic Duty',
        content='Discuss',
        author=citizen_user,
        organization=org,
        is_approved=False,
    )


@pytest.mark.django_db
class TestTopicModeration:
    def test_moderator_can_reject_topic(self, api_client, moderator_user, topic, org):
        bind_client_to_org(api_client, moderator_user, org)
        response = api_client.patch(f'/api/topics/{topic.id}/moderate/', {
            'is_approved': False,
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_approved'] is False

    def test_citizen_cannot_moderate(self, api_client, citizen_user, topic, org):
        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.patch(f'/api/topics/{topic.id}/moderate/', {
            'is_approved': True,
        }, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_moderate_missing_topic_returns_404(self, api_client, moderator_user, org):
        import uuid

        bind_client_to_org(api_client, moderator_user, org)
        response = api_client.patch(f'/api/topics/{uuid.uuid4()}/moderate/', {
            'is_approved': True,
        }, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTopicVisibility:
    def test_unapproved_topic_hidden_from_public(self, api_client, topic, org):
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/topics/')
        assert response.status_code == status.HTTP_200_OK
        ids = [t['id'] for t in response.data['results']]
        assert str(topic.id) not in ids

    def test_moderator_sees_unapproved_topic(self, api_client, moderator_user, topic, org):
        bind_client_to_org(api_client, moderator_user, org)
        response = api_client.get('/api/topics/')
        ids = [t['id'] for t in response.data['results']]
        assert str(topic.id) in ids


@pytest.mark.django_db
class TestCommentModeration:
    def test_moderator_can_moderate_comment(self, api_client, moderator_user, topic, citizen_user, org):
        comment = DiscussionComment.objects.create(
            topic=topic, author=citizen_user, comment='A comment', is_approved=False, organization=org,
        )
        bind_client_to_org(api_client, moderator_user, org)
        response = api_client.patch(f'/api/comments/{comment.id}/moderate/', {
            'is_approved': True,
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_approved'] is True


@pytest.mark.django_db
class TestPendingQueue:
    def test_pending_lists_unapproved_content(self, api_client, moderator_user, topic, citizen_user, org):
        DiscussionComment.objects.create(
            topic=topic, author=citizen_user, comment='Pending comment', is_approved=False, organization=org,
        )
        bind_client_to_org(api_client, moderator_user, org)
        response = api_client.get('/api/topics/pending/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['topics']) == 1
        assert len(response.data['comments']) == 1

    def test_suspended_user_cannot_post_topic(self, api_client, citizen_user, org):
        citizen_user.is_suspended = True
        citizen_user.save(update_fields=['is_suspended'])
        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.post('/api/topics/', {
            'title': 'Should fail',
            'content': 'Body',
        }, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
