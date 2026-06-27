import pytest
from django.core.management import call_command

from apps.accounts.models import Role
from apps.tenants.models import Membership
from apps.tenants.services import create_organization_with_owner


@pytest.mark.django_db
class TestDemoteLegacyOrgAdmins:
    def test_demotes_org_owner_with_platform_admin_role(self, django_user_model, roles):
        user = django_user_model.objects.create_user(
            email='legacy-owner@test.com',
            password='TestPass123!',
            first_name='Legacy',
            last_name='Owner',
            role=Role.objects.get(name='admin'),
        )
        create_organization_with_owner(name='Legacy Org', owner=user, slug='legacy-org')

        call_command('demote_legacy_org_admins')

        user.refresh_from_db()
        assert user.role.name == 'editor'

    def test_keeps_superuser_platform_admin(self, django_user_model, roles):
        user = django_user_model.objects.create_user(
            email='super@test.com',
            password='TestPass123!',
            first_name='Super',
            last_name='Admin',
            role=Role.objects.get(name='admin'),
            is_superuser=True,
        )
        create_organization_with_owner(name='Super Org', owner=user, slug='super-org')

        call_command('demote_legacy_org_admins')

        user.refresh_from_db()
        assert user.role.name == 'admin'

    def test_dry_run_does_not_change_roles(self, django_user_model, roles):
        user = django_user_model.objects.create_user(
            email='dry-run@test.com',
            password='TestPass123!',
            first_name='Dry',
            last_name='Run',
            role=Role.objects.get(name='admin'),
        )
        create_organization_with_owner(name='Dry Org', owner=user, slug='dry-org')

        call_command('demote_legacy_org_admins', '--dry-run')

        user.refresh_from_db()
        assert user.role.name == 'admin'
        assert Membership.objects.filter(user=user, role=Membership.OWNER).exists()
