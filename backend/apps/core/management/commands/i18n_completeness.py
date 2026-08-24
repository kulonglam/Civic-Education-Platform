"""Management command: report English/Arabic bilingual content completeness.

Usage:
    python manage.py i18n_completeness
    python manage.py i18n_completeness --format json

Reports, for each tenant-owned model with ``*_ar`` bilingual fields, how many
rows are missing Arabic translations. The platform supports English and Arabic only.
"""

from __future__ import annotations

import json

from django.core.management.base import BaseCommand

from apps.core.i18n_report import build_translation_completeness


class Command(BaseCommand):
    help = 'Report Arabic translation completeness across content models.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['table', 'json'],
            default='table',
            help='Output format (default: table)',
        )
        parser.add_argument(
            '--org',
            default=None,
            help='Filter to a single organization slug',
        )

    def handle(self, *args, **options):
        fmt = options['format']
        payload = build_translation_completeness(org_slug=options['org'])
        report = payload['rows']

        if fmt == 'json':
            self.stdout.write(json.dumps(payload, indent=2))
            return

        # Table output
        header = f"{'Model':<30} {'Field':<22} {'Total':>6} {'Done':>6} {'Missing':>8} {'%':>7}"
        self.stdout.write(self.style.HTTP_INFO(header))
        self.stdout.write('-' * len(header))

        for row in report:
            pct = row['completeness_pct']
            color = self.style.SUCCESS if pct == 100 else (
                self.style.WARNING if pct >= 50 else self.style.ERROR
            )
            line = (
                f"{row['model']:<30} {row['field']:<22}"
                f" {row['total']:>6} {row['translated']:>6}"
                f" {row['missing']:>8} {pct:>6}%"
            )
            self.stdout.write(color(line))

        if not report:
            self.stdout.write(self.style.WARNING('No bilingual models found or no rows in DB.'))
        else:
            self.stdout.write('')
            status = self.style.SUCCESS if payload['overall_pct'] == 100 else self.style.WARNING
            self.stdout.write(status(
                f"Overall: {payload['overall_translated']}/{payload['overall_total']} "
                f"fields translated ({payload['overall_pct']}%)"
            ))
