from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from apps.audit.models import ActivityLog
from apps.tenants.models import Organization


class Command(BaseCommand):
    help = 'Purge activity logs older than each organization audit_retention_days setting.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        total = 0
        for org in Organization.objects.exclude(audit_retention_days=0):
            cutoff = timezone.now() - timedelta(days=org.audit_retention_days)
            qs = ActivityLog.objects.filter(organization=org, timestamp__lt=cutoff)
            count = qs.count()
            if count and not dry_run:
                qs.delete()
            total += count
            self.stdout.write(f'{org.slug}: {count} log(s) older than {org.audit_retention_days} days')

        # Platform-wide logs with no org: keep 365 days by default
        cutoff = timezone.now() - timedelta(days=365)
        orphan = ActivityLog.objects.filter(organization__isnull=True, timestamp__lt=cutoff)
        orphan_count = orphan.count()
        if orphan_count and not dry_run:
            orphan.delete()
        total += orphan_count
        self.stdout.write(self.style.SUCCESS(f'Total purged: {total}{" (dry-run)" if dry_run else ""}'))
