import pytest
from rest_framework import status

from apps.accounts.models import UserProfile
from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org


@pytest.mark.django_db
class TestLeaderboard:
    def test_ranks_org_members_by_xp(self, api_client, org, citizen_user, django_user_model):
        profile, _ = UserProfile.objects.get_or_create(user=citizen_user)
        profile.xp_points = 40
        profile.save(update_fields=['xp_points'])

        rival = django_user_model.objects.create_user(
            email='rival@xp.test',
            password='TestPass123!',
            first_name='Nyandeng',
            last_name='Deng',
        )
        Membership.objects.create(organization=org, user=rival, role=Membership.MEMBER)
        rival_profile, _ = UserProfile.objects.get_or_create(user=rival)
        rival_profile.xp_points = 120
        rival_profile.save(update_fields=['xp_points'])

        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.get('/api/gamification/leaderboard/')
        assert response.status_code == status.HTTP_200_OK
        names = [row['display_name'] for row in response.data['entries']]
        assert names[0].startswith('Nyandeng')
        assert response.data['me']['rank'] == 2
        assert '@' not in ''.join(names)

    def test_opt_out_hides_other_learners(self, api_client, org, citizen_user, django_user_model):
        hidden = django_user_model.objects.create_user(
            email='hidden@xp.test',
            password='TestPass123!',
            first_name='Hidden',
            last_name='User',
        )
        Membership.objects.create(organization=org, user=hidden, role=Membership.MEMBER)
        profile, _ = UserProfile.objects.get_or_create(user=hidden)
        profile.xp_points = 500
        profile.show_on_leaderboard = False
        profile.save(update_fields=['xp_points', 'show_on_leaderboard'])

        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.get('/api/gamification/leaderboard/')
        names = [row['display_name'] for row in response.data['entries']]
        assert all('Hidden' not in name for name in names)
