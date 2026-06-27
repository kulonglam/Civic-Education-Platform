from django.core.management.base import BaseCommand

from apps.audit.models import ActivityLog
from apps.tenants.models import Membership


class Command(BaseCommand):
    help = 'Backfill organization on audit logs created before tenant scoping was added'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report rows that would be updated without saving',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        logs = ActivityLog.objects.filter(organization__isnull=True).select_related('user')
        updated = 0
        skipped = 0

        for log in logs.iterator():
            organization = self._resolve_organization(log)
            if organization is None:
                skipped += 1
                continue
            updated += 1
            if dry_run:
                self.stdout.write(f'[dry-run] {log.id} → {organization.slug}')
            else:
                log.organization = organization
                log.save(update_fields=['organization'])

        prefix = 'Would update' if dry_run else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'{prefix} {updated} log(s); skipped {skipped} without a resolvable org.'))

    def _resolve_organization(self, log):
        metadata = log.metadata or {}
        org_id = metadata.get('organization_id')
        if org_id:
            from apps.tenants.models import Organization

            org = Organization.objects.filter(id=org_id).first()
            if org:
                return org

        if log.user_id is None:
            return None

        membership = (
            Membership.objects.filter(user_id=log.user_id)
            .select_related('organization')
            .order_by('-created_at')
            .first()
        )
        return membership.organization if membership else None
