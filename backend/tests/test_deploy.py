"""Deployment readiness checks (production settings validation)."""

from django.test import override_settings

from apps.core.checks import production_security_checks


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
