import json
import os
import sys
import urllib.error
import urllib.request

from django.core.management.base import BaseCommand

from apps.core.safe_http import assert_http_url, safe_urlopen


class Command(BaseCommand):
    help = 'Smoke-test a running API (health, readiness, billing plans, demo articles)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--base-url',
            default=os.environ.get('SMOKE_BASE_URL', 'http://127.0.0.1:8000'),
            help='API origin without trailing slash (default: SMOKE_BASE_URL or http://127.0.0.1:8000)',
        )
        parser.add_argument(
            '--tenant-slug',
            default=os.environ.get('SMOKE_TENANT_SLUG', 'platform-demo'),
            help='Organization slug for tenant-scoped public reads',
        )

    def handle(self, *args, **options):
        base = assert_http_url(options['base_url'].rstrip('/'), allow_http=True)
        tenant = options['tenant_slug']
        failures = []

        checks = [
            ('GET', f'{base}/api/health/', {}, None),
            ('GET', f'{base}/api/ready/', {}, None),
            ('GET', f'{base}/api/billing/plans/', {}, None),
            (
                'GET',
                f'{base}/api/articles/',
                {'X-Organization-Slug': tenant},
                lambda body: _has_results(body),
            ),
            (
                'GET',
                f'{base}/api/organization/by-slug/{tenant}/',
                {},
                lambda body: body.get('slug') == tenant,
            ),
        ]

        for method, url, headers, validator in checks:
            try:
                body = _request(method, url, headers)
                if validator and not validator(body):
                    failures.append(f'{url} — unexpected response shape')
                    self.stderr.write(self.style.ERROR(f'FAIL {url}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'OK   {url}'))
            except Exception as exc:
                failures.append(f'{url} — {exc}')
                self.stderr.write(self.style.ERROR(f'FAIL {url}: {exc}'))

        if failures:
            self.stderr.write(self.style.ERROR(f'{len(failures)} check(s) failed.'))
            sys.exit(1)
        self.stdout.write(self.style.SUCCESS('All smoke checks passed.'))


def _request(method, url, headers):
    req = urllib.request.Request(url, method=method, headers=headers)
    with safe_urlopen(req, timeout=15, allow_http=True) as response:
        raw = response.read().decode('utf-8')
        return json.loads(raw) if raw else {}


def _has_results(body):
    if isinstance(body, dict):
        return bool(body.get('results'))
    return isinstance(body, list) and len(body) > 0
