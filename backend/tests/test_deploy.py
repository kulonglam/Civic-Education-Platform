"""Deployment readiness checks (production settings validation)."""

from django.test import override_settings

from apps.core.checks import production_security_checks
from apps.core.host_utils import unique_hosts


def test_unique_hosts_merges_render_hostname():
    hosts = unique_hosts(
        'api.example.com',
        'civic-education-platform-66rb.onrender.com',
    )
    assert hosts == [
        'api.example.com',
        'civic-education-platform-66rb.onrender.com',
    ]


def test_unique_hosts_dedupes_and_strips():
    assert unique_hosts(' api.example.com ,api.example.com', '') == ['api.example.com']
    assert unique_hosts('') == []


def test_render_hostname_from_env(monkeypatch):
    from apps.core.host_utils import render_hostname

    monkeypatch.setenv('RENDER_EXTERNAL_HOSTNAME', 'civic-education-platform-66rb.onrender.com')
    assert render_hostname() == 'civic-education-platform-66rb.onrender.com'


def test_render_hostname_from_url(monkeypatch):
    from apps.core.host_utils import render_hostname

    monkeypatch.delenv('RENDER_EXTERNAL_HOSTNAME', raising=False)
    monkeypatch.setenv('RENDER_EXTERNAL_URL', 'https://civic-education-platform-66rb.onrender.com')
    assert render_hostname() == 'civic-education-platform-66rb.onrender.com'


def _run_checks(**settings):
    with override_settings(DEBUG=False, **settings):
        return production_security_checks(None)


def test_production_checks_pass_with_valid_settings():
    errors = _run_checks(
        SECRET_KEY='a-unique-production-secret-key-value',
        ALLOWED_HOSTS=['api.example.com'],
        CORS_ALLOWED_ORIGINS=['https://app.example.com'],
        BILLING_PROVIDER='stripe',
        CELERY_BROKER_URL='redis://redis:6379/0',
        CELERY_TASK_ALWAYS_EAGER=False,
        STRIPE_SECRET_KEY='sk_test_xxx',
        STRIPE_WEBHOOK_SECRET='whsec_xxx',
        FRONTEND_URL='https://app.example.com',
        EMAIL_HOST='smtp.example.com',
        SENTRY_DSN='https://example@sentry.io/1',
    )
    assert errors == []


def test_production_checks_reject_insecure_secret():
    errors = _run_checks(
        SECRET_KEY='django-insecure-dev-key',
        ALLOWED_HOSTS=['api.example.com'],
        CORS_ALLOWED_ORIGINS=['https://app.example.com'],
        BILLING_PROVIDER='stripe',
        CELERY_BROKER_URL='redis://redis:6379/0',
        CELERY_TASK_ALWAYS_EAGER=False,
        STRIPE_SECRET_KEY='sk_test_xxx',
        STRIPE_WEBHOOK_SECRET='whsec_xxx',
    )
    assert any(error.id == 'core.E001' for error in errors)


def test_production_checks_reject_dummy_billing():
    errors = _run_checks(
        SECRET_KEY='a-unique-production-secret-key-value',
        ALLOWED_HOSTS=['api.example.com'],
        CORS_ALLOWED_ORIGINS=['https://app.example.com'],
        BILLING_PROVIDER='dummy',
        CELERY_BROKER_URL='redis://redis:6379/0',
        CELERY_TASK_ALWAYS_EAGER=False,
    )
    assert any(error.id == 'core.E004' for error in errors)
