import pytest
from rest_framework import status

from apps.billing.models import Plan, Subscription
from apps.billing.services import (
    apply_checkout_completed,
    apply_subscription_deleted,
    apply_subscription_updated,
)
from apps.tenants.models import Membership, Organization
from apps.tenants.services import create_organization_with_owner
from tests.conftest import login_user


@pytest.mark.django_db
class TestOrganizationRegistration:
    def test_register_creates_organization(self, api_client, roles):
        Plan.objects.create(code='free', name='Free', price_cents=0, sort_order=0)
        response = api_client.post('/api/auth/register/', {
            'email': 'saas@test.com',
            'first_name': 'SaaS',
            'last_name': 'Owner',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'account_type': 'organization',
            'organization_name': 'Acme Civic',
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert Organization.objects.filter(name='Acme Civic').exists()
        assert Membership.objects.filter(user__email='saas@test.com', role=Membership.OWNER).exists()
        assert Subscription.objects.filter(organization__name='Acme Civic').exists()

        from apps.accounts.models import User

        owner = User.objects.get(email='saas@test.com')
        assert owner.role.name == 'editor'

    def test_org_owner_cannot_access_platform_analytics(self, api_client, roles):
        Plan.objects.create(code='free', name='Free', price_cents=0, sort_order=0)
        api_client.post('/api/auth/register/', {
            'email': 'orgowner@test.com',
            'first_name': 'Org',
            'last_name': 'Owner',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'account_type': 'organization',
            'organization_name': 'Owner Org',
        })
        from apps.accounts.models import User
        from apps.tenants.models import Organization

        owner = User.objects.get(email='orgowner@test.com')
        org = Organization.objects.get(name='Owner Org')
        login = api_client.post('/api/auth/login/', {
            'email': 'orgowner@test.com',
            'password': 'SecurePass123!',
        })
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}',
            HTTP_X_TENANT_SLUG=org.slug,
        )
        response = api_client.get('/api/analytics/overview/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestMyOrganizations:
    def test_list_user_organizations(self, api_client, org, citizen_user):
        api_client.force_authenticate(user=citizen_user)
        response = api_client.get(
            '/api/organization/mine/',
            HTTP_X_TENANT_SLUG=org.slug,
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['organization']['slug'] == org.slug


@pytest.mark.django_db
class TestTenantIsolation:
    def test_jwt_cannot_spoof_foreign_tenant_header(self, api_client, org, editor_user, roles, django_user_model):
        """
        The tenant middleware must ignore X-Tenant-Slug for orgs the user
        doesn't belong to — articles always land in the JWT org.
        Uses a same-org category so only the tenant-routing logic is tested here;
        cross-tenant category injection is covered by test_cross_tenant_category_id_is_rejected.
        """
        from apps.learning.models import Article, Category

        Membership.objects.create(organization=org, user=editor_user, role=Membership.MEMBER)
        # Category belongs to the correct org so the article can be created
        own_category = Category.objects.create(organization=org, name='Own Cat', slug='own-cat')

        other_owner = django_user_model.objects.create_user(
            email='victim@test.com',
            password='TestPass123!',
            first_name='Victim',
            last_name='Owner',
        )
        other_org = create_organization_with_owner(name='Victim Org', owner=other_owner, slug='victim-org')

        login = api_client.post('/api/auth/login/', {
            'email': editor_user.email,
            'password': 'TestPass123!',
        }, format='json')
        assert login.status_code == status.HTTP_200_OK

        # User sets X-Tenant-Slug to an org they're NOT a member of — middleware
        # must fall back to the JWT org (org), not victim-org.
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}',
            HTTP_X_TENANT_SLUG='victim-org',
        )
        response = api_client.post('/api/articles/', {
            'title': 'Injected article',
            'content': 'Malicious body',
            'category_id': str(own_category.id),
            'status': 'draft',
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        # Article must land in the JWT org, never in victim-org
        assert Article.all_objects.filter(organization=other_org, title='Injected article').exists() is False
        assert Article.all_objects.filter(organization=org, title='Injected article').exists() is True

    def test_cross_tenant_category_id_is_rejected(self, api_client, org, editor_user, roles, django_user_model):
        """An article cannot reference a category that belongs to a different org."""
        from apps.learning.models import Article, Category

        Membership.objects.create(organization=org, user=editor_user, role=Membership.MEMBER)

        other_owner = django_user_model.objects.create_user(
            email='catowner@test.com',
            password='TestPass123!',
            first_name='Cat',
            last_name='Owner',
        )
        other_org = create_organization_with_owner(
            name='Other Org', owner=other_owner, slug='other-org-cat'
        )
        foreign_category = Category.objects.create(
            organization=other_org, name='Foreign Cat', slug='foreign-cat'
        )

        login = api_client.post('/api/auth/login/', {
            'email': editor_user.email,
            'password': 'TestPass123!',
        }, format='json')
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}',
            HTTP_X_TENANT_SLUG=org.slug,
        )

        # Article with a category from a foreign org should be rejected with 400
        response = api_client.post('/api/articles/', {
            'title': 'Foreign Category Article',
            'content': 'Body',
            'category_id': str(foreign_category.id),
            'status': 'draft',
        }, format='json')
        assert response.status_code == 400, (
            'Expected 400 when category_id belongs to a different org, '
            f'got {response.status_code}: {response.data}'
        )
        assert Article.all_objects.filter(title='Foreign Category Article').exists() is False

    def test_member_can_switch_org_via_header(self, api_client, org, citizen_user, django_user_model):
        """Org switcher: header selects another org the user belongs to."""
        second_owner = django_user_model.objects.create_user(
            email='second@test.com',
            password='TestPass123!',
            first_name='Second',
            last_name='Org',
        )
        second_org = create_organization_with_owner(name='Second Org', owner=second_owner, slug='second-org')
        Membership.objects.create(organization=second_org, user=citizen_user, role=Membership.MEMBER)

        login = login_user(api_client, citizen_user)
        assert login.status_code == status.HTTP_200_OK

        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}',
            HTTP_X_TENANT_SLUG='second-org',
        )
        response = api_client.get('/api/organization/current/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['slug'] == 'second-org'

    def test_articles_scoped_to_tenant(self, api_client, org, editor_user, roles, django_user_model):
        from apps.learning.models import Article, Category

        other_owner = django_user_model.objects.create_user(
            email='other@test.com',
            password='TestPass123!',
            first_name='Other',
            last_name='Org',
        )
        other_org = create_organization_with_owner(name='Other Org', owner=other_owner, slug='other-org')

        cat_a = Category.objects.create(organization=org, name='Cat A', slug='cat-a')
        cat_b = Category.objects.create(organization=other_org, name='Cat B', slug='cat-b')
        Article.objects.create(
            title='Org A Article',
            content='A',
            category=cat_a,
            author=editor_user,
            organization=org,
            status='published',
        )
        Article.objects.create(
            title='Org B Article',
            content='B',
            category=cat_b,
            author=other_owner,
            organization=other_org,
            status='published',
        )

        api_client.credentials(HTTP_X_TENANT_SLUG='test-org')
        response = api_client.get('/api/articles/')
        assert response.status_code == status.HTTP_200_OK
        titles = [a['title'] for a in response.data['results']]
        assert 'Org A Article' in titles
        assert 'Org B Article' not in titles


@pytest.mark.django_db
class TestBilling:
    def test_list_plans_public(self, api_client, db):
        Plan.objects.create(code='free', name='Free', price_cents=0, sort_order=0)
        response = api_client.get('/api/billing/plans/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_checkout_upgrades_plan(self, api_client, org, citizen_user):
        free = Plan.objects.create(code='free', name='Free', price_cents=0, sort_order=0, max_articles=1)
        pro = Plan.objects.create(code='pro', name='Pro', price_cents=2900, sort_order=1, max_articles=100)
        Subscription.objects.create(organization=org, plan=free, status=Subscription.ACTIVE)

        api_client.force_authenticate(user=citizen_user)
        api_client.credentials(HTTP_X_TENANT_SLUG='test-org')
        response = api_client.post('/api/billing/checkout/', {'plan_code': 'pro'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        sub = Subscription.objects.get(organization=org)
        assert sub.plan.code == 'pro'

    def test_stripe_checkout_does_not_upgrade_before_webhook(self, api_client, org, citizen_user, settings):
        free = Plan.objects.create(code='free', name='Free', price_cents=0, sort_order=0)
        Plan.objects.create(code='pro', name='Pro', price_cents=2900, sort_order=1, max_articles=100)
        Subscription.objects.create(organization=org, plan=free, status=Subscription.ACTIVE)

        settings.BILLING_PROVIDER = 'stripe'
        settings.STRIPE_SECRET_KEY = 'sk_test_xxx'
        settings.STRIPE_PRICE_IDS = {'pro': 'price_test_pro'}

        api_client.force_authenticate(user=citizen_user)
        api_client.credentials(HTTP_X_TENANT_SLUG='test-org')

        class FakeStripeProvider:
            def create_customer(self, organization, email):
                return 'cus_test'

            def create_checkout_session(self, subscription, plan, success_url, cancel_url):
                from apps.billing.providers import CheckoutResult

                return CheckoutResult(url='https://checkout.stripe.test/session', activate_immediately=False)

        from apps.billing import views as billing_views

        original = billing_views.get_billing_provider
        billing_views.get_billing_provider = lambda: FakeStripeProvider()
        try:
            response = api_client.post('/api/billing/checkout/', {'plan_code': 'pro'}, format='json')
        finally:
            billing_views.get_billing_provider = original

        assert response.status_code == status.HTTP_200_OK
        sub = Subscription.objects.get(organization=org)
        assert sub.plan.code == 'free'
        assert sub.provider_customer_id == 'cus_test'

    def test_subscription_endpoint_creates_missing_free_subscription(self, api_client, org, citizen_user):
        Plan.objects.create(code='free', name='Free', price_cents=0, sort_order=0, max_members=5)

        api_client.force_authenticate(user=citizen_user)
        api_client.credentials(HTTP_X_TENANT_SLUG='test-org')
        response = api_client.get('/api/billing/subscription/')
        assert response.status_code == status.HTTP_200_OK
        assert Subscription.objects.filter(organization=org, plan__code='free').exists()


@pytest.mark.django_db
class TestStripeWebhooks:
    def test_checkout_completed_activates_plan(self, org):
        free = Plan.objects.create(code='free', name='Free', price_cents=0, sort_order=0)
        pro = Plan.objects.create(code='pro', name='Pro', price_cents=2900, sort_order=1)
        subscription = Subscription.objects.create(organization=org, plan=free, status=Subscription.ACTIVE)

        apply_checkout_completed({
            'metadata': {
                'organization_id': str(org.id),
                'plan_code': 'pro',
            },
            'subscription': 'sub_test_123',
            'customer': 'cus_test_123',
        })

        subscription.refresh_from_db()
        assert subscription.plan_id == pro.id
        assert subscription.status == Subscription.ACTIVE
        assert subscription.provider_subscription_id == 'sub_test_123'
        assert subscription.provider_customer_id == 'cus_test_123'

    def test_subscription_deleted_downgrades_to_free(self, org, settings):
        free = Plan.objects.create(code='free', name='Free', price_cents=0, sort_order=0)
        pro = Plan.objects.create(code='pro', name='Pro', price_cents=2900, sort_order=1)
        subscription = Subscription.objects.create(
            organization=org,
            plan=pro,
            status=Subscription.ACTIVE,
            provider_subscription_id='sub_test_123',
        )

        apply_subscription_deleted({'id': 'sub_test_123'})

        subscription.refresh_from_db()
        assert subscription.plan_id == free.id
        assert subscription.status == Subscription.CANCELED

    def test_subscription_updated_maps_price_to_plan(self, org, settings):
        free = Plan.objects.create(code='free', name='Free', price_cents=0, sort_order=0)
        pro = Plan.objects.create(code='pro', name='Pro', price_cents=2900, sort_order=1)
        subscription = Subscription.objects.create(
            organization=org,
            plan=free,
            status=Subscription.ACTIVE,
            provider_subscription_id='sub_test_456',
        )
        settings.STRIPE_PRICE_IDS = {'pro': 'price_test_pro'}

        apply_subscription_updated({
            'id': 'sub_test_456',
            'status': 'active',
            'customer': 'cus_test_456',
            'metadata': {'organization_id': str(org.id)},
            'items': {'data': [{'price': {'id': 'price_test_pro'}}]},
        })

        subscription.refresh_from_db()
        assert subscription.plan_id == pro.id
        assert subscription.status == Subscription.ACTIVE


@pytest.mark.django_db
class TestQuotas:
    def test_article_quota_enforced(self, api_client, org, editor_user, roles):
        from apps.billing.models import Plan, Subscription
        from apps.learning.models import Article, Category
        from apps.tenants.models import Membership

        Membership.objects.create(organization=org, user=editor_user, role=Membership.MEMBER)
        plan = Plan.objects.create(code='free', name='Free', max_articles=1, price_cents=0)
        Subscription.objects.create(organization=org, plan=plan, status=Subscription.ACTIVE)
        category = Category.objects.create(organization=org, name='C', slug='c')
        Article.objects.create(
            title='Existing',
            content='x',
            category=category,
            author=editor_user,
            organization=org,
            status='draft',
        )

        api_client.force_authenticate(user=editor_user)
        api_client.credentials(HTTP_X_TENANT_SLUG='test-org')
        response = api_client.post('/api/articles/', {
            'title': 'Over quota',
            'content': 'Body',
            'category_id': str(category.id),
            'status': 'draft',
        }, format='json')
        assert response.status_code == status.HTTP_402_PAYMENT_REQUIRED
