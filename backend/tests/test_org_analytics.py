import pytest
from rest_framework import status

from apps.accounts.models import Role
from apps.billing.models import Plan, Subscription
from apps.quizzes.models import Quiz, QuizAttempt
from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org


@pytest.fixture
def pro_plan(db):
    return Plan.objects.create(
        code='pro',
        name='Pro',
        price_cents=2900,
        sort_order=1,
        features={'analytics': True},
    )


@pytest.fixture
def free_plan(db):
    return Plan.objects.create(
        code='free',
        name='Free',
        price_cents=0,
        sort_order=0,
        features={'analytics': False},
    )


@pytest.fixture
def org_admin_member(roles, django_user_model, org):
    user = django_user_model.objects.create_user(
        email='orgadmin@test.com',
        password='TestPass123!',
        first_name='Org',
        last_name='Admin',
    )
    Membership.objects.create(organization=org, user=user, role=Membership.ADMIN)
    return user


@pytest.mark.django_db
class TestOrgAnalytics:
    def test_dashboard_requires_paid_plan(self, api_client, org, org_admin_member, free_plan):
        Subscription.objects.create(organization=org, plan=free_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, org_admin_member, org, membership_role=Membership.ADMIN)

        response = api_client.get('/api/analytics/dashboard/')
        assert response.status_code == status.HTTP_402_PAYMENT_REQUIRED

    def test_dashboard_available_on_pro_plan(self, api_client, org, org_admin_member, pro_plan):
        Subscription.objects.create(organization=org, plan=pro_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, org_admin_member, org, membership_role=Membership.ADMIN)

        response = api_client.get('/api/analytics/dashboard/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total_members' in response.data
        assert response.data['total_members'] >= 1

    def test_member_progress_lists_org_members(self, api_client, org, org_admin_member, citizen_user, pro_plan):
        Subscription.objects.create(organization=org, plan=pro_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, citizen_user, org)
        bind_client_to_org(api_client, org_admin_member, org, membership_role=Membership.ADMIN)

        quiz = Quiz.objects.create(title='Civic Basics', organization=org)
        QuizAttempt.objects.create(
            quiz=quiz,
            user=citizen_user,
            organization=org,
            score=80,
            max_score=100,
            passed=True,
        )

        response = api_client.get('/api/analytics/progress/')
        assert response.status_code == status.HTTP_200_OK
        emails = [row['email'] for row in response.data['members']]
        assert 'citizen@test.com' in emails
        citizen_row = next(row for row in response.data['members'] if row['email'] == 'citizen@test.com')
        assert citizen_row['quizzes_attempted'] == 1
        assert citizen_row['quizzes_passed'] == 1

    def test_csv_export(self, api_client, org, org_admin_member, pro_plan):
        Subscription.objects.create(organization=org, plan=pro_plan, status=Subscription.ACTIVE)
        bind_client_to_org(api_client, org_admin_member, org, membership_role=Membership.ADMIN)

        response = api_client.get('/api/analytics/export/csv/')
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'
        assert 'attachment; filename="test-org-progress.csv"' in response['Content-Disposition']
        body = response.content.decode('utf-8')
        assert body.startswith('email,first_name,last_name')
        assert 'orgadmin@test.com' in body

    def test_citizen_member_cannot_access_dashboard(self, api_client, org, roles, django_user_model, pro_plan):
        Subscription.objects.create(organization=org, plan=pro_plan, status=Subscription.ACTIVE)
        member = django_user_model.objects.create_user(
            email='member-only@test.com',
            password='TestPass123!',
            first_name='Regular',
            last_name='Member',
        )
        bind_client_to_org(api_client, member, org, membership_role=Membership.MEMBER)

        response = api_client.get('/api/analytics/dashboard/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_org_owner_with_editor_role_can_access_dashboard(
        self, api_client, org, roles, django_user_model, pro_plan
    ):
        Subscription.objects.create(organization=org, plan=pro_plan, status=Subscription.ACTIVE)
        editor_role = Role.objects.get(name='editor')
        owner = django_user_model.objects.create_user(
            email='owner-editor@test.com',
            password='TestPass123!',
            first_name='Owner',
            last_name='Editor',
            role=editor_role,
        )
        bind_client_to_org(api_client, owner, org, membership_role=Membership.OWNER)

        response = api_client.get('/api/analytics/dashboard/')
        assert response.status_code == status.HTTP_200_OK
