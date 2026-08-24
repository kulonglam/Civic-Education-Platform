import pytest
from rest_framework import status

from apps.accounts.models import UserProfile
from apps.engagement.models import Poll, PollOption, PollVote
from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org


def _open_poll(org, user, *, kind=Poll.KIND_COMMUNITY, question='Biggest community challenge?'):
    poll = Poll.objects.create(
        organization=org,
        question=question,
        kind=kind,
        status=Poll.STATUS_OPEN,
        created_by=user,
    )
    PollOption.objects.create(organization=org, poll=poll, label='Education', sort_order=0)
    PollOption.objects.create(organization=org, poll=poll, label='Health', sort_order=1)
    return poll


@pytest.mark.django_db
class TestPolls:
    def test_list_includes_kind_and_hides_results_before_vote(self, api_client, citizen_user, org):
        poll = _open_poll(
            org,
            citizen_user,
            kind=Poll.KIND_EDUCATIONAL,
            question='Do citizens understand this new policy?',
        )
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)
        response = api_client.get('/api/engagement/polls/')
        assert response.status_code == status.HTTP_200_OK
        row = next(item for item in response.data if item['id'] == str(poll.id))
        assert row['kind'] == 'educational'
        assert row['results_visible'] is False
        assert 'vote_count' not in row['options'][0]

    def test_vote_snapshots_region_and_shows_results(self, api_client, citizen_user, org):
        poll = _open_poll(org, citizen_user)
        profile, _ = UserProfile.objects.get_or_create(user=citizen_user)
        profile.region = 'central_equatoria'
        profile.age_band = '25_34'
        profile.save(update_fields=['region', 'age_band'])
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)
        option_id = poll.options.order_by('sort_order').first().id
        response = api_client.post(
            f'/api/engagement/polls/{poll.id}/vote/',
            {'option_id': str(option_id)},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results_visible'] is True
        assert response.data['total_votes'] == 1
        vote = PollVote.objects.get(poll=poll, user=citizen_user)
        assert vote.region == 'central_equatoria'
        assert vote.age_band == '25_34'

    def test_filter_community_polls(self, api_client, citizen_user, org):
        _open_poll(org, citizen_user, kind=Poll.KIND_COMMUNITY, question='Which public service needs improvement?')
        _open_poll(org, citizen_user, kind=Poll.KIND_EDUCATIONAL, question='Do citizens understand this new policy?')
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)
        response = api_client.get('/api/engagement/polls/', {'kind': 'community'})
        assert response.status_code == status.HTTP_200_OK
        assert all(row['kind'] == 'community' for row in response.data)
        assert any('public service' in row['question'] for row in response.data)


@pytest.mark.django_db
class TestPollOpinionAnalytics:
    def test_admin_sees_totals_and_suppresses_small_regions(
        self, api_client, admin_user, citizen_user, django_user_model, org,
    ):
        poll = _open_poll(org, admin_user, question='What is the biggest challenge in your community?')
        education = poll.options.get(label='Education')
        health = poll.options.get(label='Health')

        def vote(user, option, region, age_band='25_34'):
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.region = region
            profile.age_band = age_band
            profile.save(update_fields=['region', 'age_band'])
            PollVote.objects.create(
                organization=org,
                poll=poll,
                option=option,
                user=user,
                region=region,
                age_band=age_band,
            )
            option.vote_count += 1
            option.save(update_fields=['vote_count'])

        vote(citizen_user, education, 'central_equatoria')
        extra_users = []
        for index in range(4):
            user = django_user_model.objects.create_user(
                email=f'poll-voter-{index}@test.com',
                password='TestPass123!',
                first_name='Voter',
                last_name=str(index),
            )
            extra_users.append(user)
            Membership.objects.create(organization=org, user=user, role=Membership.MEMBER)
        vote(extra_users[0], education, 'central_equatoria')
        vote(extra_users[1], education, 'central_equatoria')
        vote(extra_users[2], health, 'jonglei', '18_24')
        vote(extra_users[3], health, 'jonglei', '18_24')

        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)
        blocked = api_client.get('/api/analytics/polls/')
        assert blocked.status_code == status.HTTP_403_FORBIDDEN

        bind_client_to_org(api_client, admin_user, org)
        response = api_client.get('/api/analytics/polls/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_responses'] >= 5
        row = next(item for item in response.data['polls'] if item['id'] == str(poll.id))
        assert row['total_votes'] == 5
        assert row['demographics_available'] is True
        region_keys = {item['key']: item['count'] for item in row['regions']}
        assert region_keys['central_equatoria'] == 3
        assert 'jonglei' not in region_keys
        assert region_keys['suppressed'] == 2


@pytest.mark.django_db
class TestPollManagement:
    def test_drafts_hidden_until_manage(self, api_client, citizen_user, editor_user, org):
        Poll.objects.create(
            organization=org,
            question='Draft poll?',
            status=Poll.STATUS_DRAFT,
            created_by=editor_user,
        )
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)
        public = api_client.get('/api/engagement/polls/')
        assert public.status_code == status.HTTP_200_OK
        assert all(row['question'] != 'Draft poll?' for row in public.data)

        bind_client_to_org(api_client, editor_user, org, membership_role=Membership.CONTENT_MANAGER)
        managed = api_client.get('/api/engagement/polls/', {'manage': '1'})
        assert managed.status_code == status.HTTP_200_OK
        assert any(row['question'] == 'Draft poll?' for row in managed.data)

    def test_editor_creates_and_updates_poll(self, api_client, editor_user, org):
        bind_client_to_org(api_client, editor_user, org, membership_role=Membership.CONTENT_MANAGER)
        created = api_client.post(
            '/api/engagement/polls/',
            {
                'question': 'Which civic skill should we teach next?',
                'kind': 'educational',
                'status': 'open',
                'options': [
                    {'label': 'Budget literacy'},
                    {'label': 'Peacebuilding'},
                ],
            },
            format='json',
        )
        assert created.status_code == status.HTTP_201_CREATED, created.data
        poll_id = created.data['id']
        updated = api_client.patch(
            f'/api/engagement/polls/{poll_id}/',
            {'question': 'Which civic skill should we teach first?'},
            format='json',
        )
        assert updated.status_code == status.HTTP_200_OK
        assert updated.data['question'] == 'Which civic skill should we teach first?'
        assert len(updated.data['options']) == 2


@pytest.mark.django_db
class TestCampaignJoin:
    def test_member_can_join_active_campaign(self, api_client, citizen_user, org):
        from apps.engagement.models import Campaign

        campaign = Campaign.objects.create(
            organization=org,
            title='Voter education week',
            description='Join neighbours for civic learning.',
            status=Campaign.STATUS_ACTIVE,
            created_by=citizen_user,
        )
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)
        response = api_client.post(f'/api/engagement/campaigns/{campaign.id}/join/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user_joined'] is True
        assert response.data['signup_count'] == 1
