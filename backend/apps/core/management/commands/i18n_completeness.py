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


# Models and their (english_field, arabic_field) bilingual pairs
BILINGUAL_MODELS = [
    ('learning', 'Article',   [('title', 'title_ar'), ('content', 'content_ar')]),
    ('learning', 'Category',  [('name', 'name_ar')]),
    ('quizzes',  'Quiz',      [('title', 'title_ar')]),
    ('quizzes',  'Question',  [('text',  'text_ar')]),
]


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
        from django.apps import apps

        fmt = options['format']
        org_slug = options['org']
        report = []

        for app_label, model_name, pairs in BILINGUAL_MODELS:
            try:
                model = apps.get_model(app_label, model_name)
            except LookupError:
                continue

            qs = getattr(model, 'all_objects', model.objects).all()
            if org_slug:
                qs = qs.filter(organization__slug=org_slug)

            total = qs.count()
            if total == 0:
                continue

            for en_field, ar_field in pairs:
                empty = qs.filter(**{f'{ar_field}__in': ['', None]}).count()
                pct = round((total - empty) / total * 100, 1) if total else 0.0
                report.append({
                    'model': f'{app_label}.{model_name}',
                    'field': ar_field,
                    'total': total,
                    'translated': total - empty,
                    'missing': empty,
                    'completeness_pct': pct,
                })

        if fmt == 'json':
            self.stdout.write(json.dumps(report, indent=2))
            return

        # Table output
        header = f"{'Model':<30} {'Field':<15} {'Total':>6} {'Done':>6} {'Missing':>8} {'%':>7}"
        self.stdout.write(self.style.HTTP_INFO(header))
        self.stdout.write('-' * len(header))

        for row in report:
            pct = row['completeness_pct']
            color = self.style.SUCCESS if pct == 100 else (
                self.style.WARNING if pct >= 50 else self.style.ERROR
            )
            line = (
                f"{row['model']:<30} {row['field']:<15}"
                f" {row['total']:>6} {row['translated']:>6}"
                f" {row['missing']:>8} {pct:>6}%"
            )
            self.stdout.write(color(line))

        if not report:
            self.stdout.write(self.style.WARNING('No bilingual models found or no rows in DB.'))
        else:
            overall_missing = sum(r['missing'] for r in report)
            overall_total = sum(r['total'] for r in report)
            overall_pct = round((overall_total - overall_missing) / overall_total * 100, 1) if overall_total else 0
            self.stdout.write('')
            status = self.style.SUCCESS if overall_pct == 100 else self.style.WARNING
            self.stdout.write(status(
                f'Overall: {overall_total - overall_missing}/{overall_total} fields translated ({overall_pct}%)'
            ))
