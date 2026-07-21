import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Role
from apps.accounts.mfa import user_requires_mfa
from apps.tenants.models import Membership
from apps.tenants.services import create_organization_with_owner

MFA_TEST_SECRET = 'JBSWY3DPEHPK3PXP'


def enable_mfa(user):
    """Enroll a test user in TOTP MFA (privileged routes require this)."""
    profile = user.profile
    profile.totp_secret = MFA_TEST_SECRET
    profile.mfa_enabled = True
    profile.save(update_fields=['totp_secret', 'mfa_enabled'])
    return user


def login_user(api_client, user, password='TestPass123!'):
    """Log in via API, completing MFA when enrolled."""
    import pyotp

    response = api_client.post('/api/auth/login/', {
        'email': user.email,
        'password': password,
    }, format='json')
    if response.status_code != 200:
        return response
    if response.data.get('mfa_required'):
        totp = pyotp.TOTP(user.profile.totp_secret)
        response = api_client.post('/api/auth/mfa/verify/', {
            'mfa_token': response.data['mfa_token'],
            'code': totp.now(),
        }, format='json')
    return response


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def roles(db):
    for name in ('citizen', 'moderator', 'editor', 'admin'):
        Role.objects.get_or_create(name=name)
    return Role.objects.all()


@pytest.fixture
def org(db, citizen_user):
    """Default tenant; citizen_user is owner."""
    org = create_organization_with_owner(name='Test Org', owner=citizen_user, slug='test-org')
    enable_mfa(citizen_user)
    return org


@pytest.fixture
def category(db, org):
    from apps.learning.models import Category

    return Category.objects.create(organization=org, name='Constitution', slug='constitution')


def bind_client_to_org(api_client, user, org, *, membership_role=Membership.MEMBER, skip_mfa=False):
    """Authenticate and scope requests to ``org`` (creates membership if needed)."""
    membership, created = Membership.objects.get_or_create(
        organization=org,
        user=user,
        defaults={'role': membership_role},
    )
    if not created and membership.role != membership_role:
        membership.role = membership_role
        membership.save(update_fields=['role'])
    api_client.force_authenticate(user=user)
    api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
    if user_requires_mfa(user) and not skip_mfa:
        enable_mfa(user)


@pytest.fixture
def citizen_user(roles, django_user_model):
    return django_user_model.objects.create_user(
        email='citizen@test.com',
        password='TestPass123!',
        first_name='Test',
        last_name='Citizen',
    )


@pytest.fixture
def editor_user(roles, django_user_model):
    role = Role.objects.get(name='editor')
    return django_user_model.objects.create_user(
        email='editor@test.com',
        password='TestPass123!',
        first_name='Test',
        last_name='Editor',
        role=role,
    )


@pytest.fixture
def moderator_user(roles, django_user_model):
    role = Role.objects.get(name='moderator')
    return django_user_model.objects.create_user(
        email='moderator@test.com',
        password='TestPass123!',
        first_name='Test',
        last_name='Moderator',
        role=role,
    )


@pytest.fixture
def admin_user(roles, django_user_model):
    role = Role.objects.get(name='admin')
    user = django_user_model.objects.create_user(
        email='admin@test.com',
        password='TestPass123!',
        first_name='Admin',
        last_name='User',
        role=role,
        is_staff=True,
    )
    return enable_mfa(user)
