import pytest
from django.core.management import call_command

from apps.audit.models import ActivityLog
from apps.audit.services import log_activity
from apps.tenants.models import Membership


@pytest.mark.django_db
class TestBackfillAuditOrgs:
    def test_backfills_from_user_membership(self, citizen_user, org):
        log = ActivityLog.objects.create(
            user=citizen_user,
            activity_type='user_login',
            metadata={},
            organization=None,
        )
        Membership.objects.get_or_create(
            organization=org,
            user=citizen_user,
            defaults={'role': Membership.MEMBER},
        )

        call_command('backfill_audit_orgs')

        log.refresh_from_db()
        assert log.organization_id == org.id

    def test_backfills_from_metadata_organization_id(self, citizen_user, org):
        log = ActivityLog.objects.create(
            user=citizen_user,
            activity_type='article_created',
            metadata={'organization_id': str(org.id)},
            organization=None,
        )

        call_command('backfill_audit_orgs')

        log.refresh_from_db()
        assert log.organization_id == org.id

    def test_dry_run_leaves_rows_unchanged(self, citizen_user, org):
        log_activity(citizen_user, 'user_login', organization=None)
        log = ActivityLog.objects.filter(organization__isnull=True).first()
        Membership.objects.get_or_create(
            organization=org,
            user=citizen_user,
            defaults={'role': Membership.MEMBER},
        )

        call_command('backfill_audit_orgs', '--dry-run')

        log.refresh_from_db()
        assert log.organization_id is None
