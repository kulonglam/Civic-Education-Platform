import json
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.integrations import (
    STATUS_DEGRADED,
    STATUS_DUMMY,
    STATUS_EAGER,
    STATUS_LIVE,
    STATUS_UNSET,
    build_integrations_report,
)


class Command(BaseCommand):
    help = 'Report configured vs live vs dummy status for production integrations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output machine-readable JSON',
        )
        parser.add_argument(
            '--strict',
            action='store_true',
            help='Exit non-zero when a required-in-production integration is not live/configured',
        )
        parser.add_argument(
            '--skip-infra',
            action='store_true',
            help='Skip database/cache/celery checks (provider config only)',
        )

    def handle(self, *args, **options):
        report = build_integrations_report(include_infra=not options['skip_infra'])
        summary = report['summary']

        if options['json']:
            self.stdout.write(json.dumps(report, indent=2, default=str))
        else:
            self.stdout.write('Integration status')
            self.stdout.write('=' * 40)
            for row in report['integrations']:
                req = ' (required)' if row.get('required_in_production') else ''
                self.stdout.write(
                    f"{row['name']:14} {row['status']:12}{req} — {row.get('detail', '')}"
                )
            self.stdout.write('')
            self.stdout.write(f"Overall: {summary['overall']}")
            if summary['required_missing']:
                self.stdout.write(f"Required missing: {', '.join(summary['required_missing'])}")
            if summary['degraded']:
                self.stdout.write(f"Degraded: {', '.join(summary['degraded'])}")
            if summary['optional_dummy']:
                self.stdout.write(f"Optional dummy/unset: {', '.join(summary['optional_dummy'])}")

        if not options['strict']:
            return

        failures: list[str] = []
        ok_statuses = {STATUS_LIVE, STATUS_CONFIGURED, STATUS_EAGER}
        for row in report['integrations']:
            if not row.get('required_in_production'):
                continue
            if row['status'] not in ok_statuses:
                failures.append(row['name'])

        if failures and not settings.DEBUG:
            if not options['json']:
                self.stderr.write(
                    self.style.ERROR(
                        f'Strict check failed for: {", ".join(failures)} '
                        '(set vars per docs/production-env-checklist.md)'
                    )
                )
            sys.exit(1)

        if summary['overall'] == STATUS_DEGRADED and not settings.DEBUG:
            sys.exit(1)
