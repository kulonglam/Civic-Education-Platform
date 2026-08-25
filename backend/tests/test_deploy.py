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


def test_production_public_origin_rejects_localhost():
    from apps.core.host_utils import production_public_origin

    assert production_public_origin('') == ''
    assert production_public_origin('http://localhost:5173') == ''
    assert production_public_origin('http://127.0.0.1:5173/') == ''
    assert (
        production_public_origin('https://civic-education-web-xxxx.onrender.com/')
        == 'https://civic-education-web-xxxx.onrender.com'
    )


def test_render_hostname_empty_without_env(monkeypatch):
    from apps.core.host_utils import render_hostname

    monkeypatch.delenv('RENDER_EXTERNAL_HOSTNAME', raising=False)
    monkeypatch.delenv('RENDER_EXTERNAL_URL', raising=False)
    assert render_hostname() == ''


def test_redis_url_points_to_localhost():
    from apps.core.host_utils import redis_url_points_to_localhost

    assert redis_url_points_to_localhost('redis://localhost:6379/0')
    assert redis_url_points_to_localhost('redis://127.0.0.1:6379/0')
    assert not redis_url_points_to_localhost('')
    assert not redis_url_points_to_localhost('redis://red-abc123:6379')


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


def test_production_checks_allow_dummy_billing_when_flag_set():
    errors = _run_checks(
        SECRET_KEY='a-unique-production-secret-key-value',
        ALLOWED_HOSTS=['api.example.com'],
        CORS_ALLOWED_ORIGINS=['https://app.example.com'],
        BILLING_PROVIDER='dummy',
        ALLOW_DUMMY_BILLING_IN_PRODUCTION=True,
        CELERY_BROKER_URL='redis://redis:6379/0',
        CELERY_TASK_ALWAYS_EAGER=False,
        EMAIL_HOST='smtp.example.com',
        SENTRY_DSN='https://example@sentry.io/1',
    )
    assert not any(error.id == 'core.E004' for error in errors)
