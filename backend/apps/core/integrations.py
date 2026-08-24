"""Runtime status for external integrations (Stripe, Celery, SMS, etc.)."""

from __future__ import annotations

import logging
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)

STATUS_LIVE = 'live'
STATUS_CONFIGURED = 'configured'
STATUS_DUMMY = 'dummy'
STATUS_UNSET = 'unset'
STATUS_DEGRADED = 'degraded'
STATUS_EAGER = 'eager'


def _entry(
    name: str,
    status: str,
    *,
    required_in_production: bool = False,
    detail: str = '',
    meta: dict | None = None,
) -> dict[str, Any]:
    return {
        'name': name,
        'status': status,
        'required_in_production': required_in_production,
        'detail': detail,
        'meta': meta or {},
    }


def check_database() -> dict[str, Any]:
    from django.db import connections
    from django.db.utils import OperationalError

    try:
        connections['default'].cursor().execute('SELECT 1')
        return _entry('database', STATUS_LIVE, required_in_production=True, detail='PostgreSQL reachable')
    except OperationalError as exc:
        return _entry(
            'database',
            STATUS_DEGRADED,
            required_in_production=True,
            detail=str(exc),
        )


def check_cache() -> dict[str, Any]:
    from django.core.cache import cache

    try:
        cache.set('integrations_probe', '1', 5)
        ok = cache.get('integrations_probe') == '1'
        return _entry(
            'cache',
            STATUS_LIVE if ok else STATUS_DEGRADED,
            required_in_production=True,
            detail='Redis/cache reachable' if ok else 'Cache read/write failed',
        )
    except Exception as exc:  # noqa: BLE001
        return _entry('cache', STATUS_DEGRADED, required_in_production=True, detail=str(exc))


def check_celery() -> dict[str, Any]:
    broker = getattr(settings, 'CELERY_BROKER_URL', '') or ''
    eager = getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False)

    if eager:
        return _entry(
            'celery',
            STATUS_EAGER,
            required_in_production=False,
            detail='CELERY_TASK_ALWAYS_EAGER=True — tasks run inline (dev/CI only)',
            meta={'broker_configured': bool(broker)},
        )

    if not broker:
        return _entry(
            'celery',
            STATUS_UNSET,
            required_in_production=True,
            detail='CELERY_BROKER_URL is not set',
        )

    try:
        from config.celery import app

        inspect = app.control.inspect(timeout=2.0)
        ping = inspect.ping() if inspect else None
        workers = sorted(ping.keys()) if ping else []
        if workers:
            return _entry(
                'celery',
                STATUS_LIVE,
                required_in_production=True,
                detail=f'{len(workers)} worker(s) responding',
                meta={'workers': workers},
            )
        return _entry(
            'celery',
            STATUS_DEGRADED,
            required_in_production=True,
            detail='Broker configured but no Celery workers responded to ping',
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning('Celery integration check failed: %s', exc)
        return _entry(
            'celery',
            STATUS_DEGRADED,
            required_in_production=True,
            detail=str(exc),
        )


def check_stripe() -> dict[str, Any]:
    provider = getattr(settings, 'BILLING_PROVIDER', 'dummy')
    if provider != 'stripe':
        allow_dummy = getattr(settings, 'ALLOW_DUMMY_BILLING_IN_PRODUCTION', False)
        if provider == 'dummy' and allow_dummy:
            return _entry(
                'stripe',
                STATUS_DUMMY,
                required_in_production=False,
                detail='BILLING_PROVIDER=dummy — payments disabled (ALLOW_DUMMY_BILLING_IN_PRODUCTION=True)',
            )
        return _entry(
            'stripe',
            STATUS_DUMMY,
            required_in_production=True,
            detail=f'BILLING_PROVIDER={provider!r} (production requires stripe or ALLOW_DUMMY_BILLING_IN_PRODUCTION=True)',
        )

    secret = getattr(settings, 'STRIPE_SECRET_KEY', '')
    webhook = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
    missing = [k for k, v in (
        ('STRIPE_SECRET_KEY', secret),
        ('STRIPE_WEBHOOK_SECRET', webhook),
    ) if not v]

    if missing:
        return _entry(
            'stripe',
            STATUS_CONFIGURED,
            required_in_production=True,
            detail=f'Missing: {", ".join(missing)}',
        )

    mode = 'test' if secret.startswith('sk_test_') else 'live' if secret.startswith('sk_live_') else 'unknown'
    return _entry(
        'stripe',
        STATUS_LIVE,
        required_in_production=True,
        detail=f'Stripe keys present ({mode} mode)',
        meta={'mode': mode},
    )


def check_email() -> dict[str, Any]:
    host = getattr(settings, 'EMAIL_HOST', '')
    if not host:
        return _entry(
            'email',
            STATUS_UNSET,
            required_in_production=True,
            detail='EMAIL_HOST is not set',
        )
    backend = getattr(settings, 'EMAIL_BACKEND', '')
    return _entry(
        'email',
        STATUS_CONFIGURED,
        required_in_production=True,
        detail=f'SMTP configured ({host})',
        meta={'backend': backend},
    )


def check_sentry() -> dict[str, Any]:
    dsn = getattr(settings, 'SENTRY_DSN', '') or ''
    if not dsn:
        require = True
        try:
            from decouple import config

            require = config('REQUIRE_SENTRY', default=True, cast=bool)
        except Exception:  # noqa: BLE001
            pass
        return _entry(
            'sentry',
            STATUS_UNSET,
            required_in_production=require,
            detail='SENTRY_DSN is not set',
        )
    return _entry(
        'sentry',
        STATUS_LIVE,
        required_in_production=True,
        detail='Sentry DSN configured',
        meta={'environment': getattr(settings, 'SENTRY_ENVIRONMENT', '')},
    )


def check_sms() -> dict[str, Any]:
    provider = getattr(settings, 'SMS_PROVIDER', 'dummy')
    if provider == 'africastalking' and settings.AT_API_KEY and settings.AT_USERNAME:
        return _entry(
            'sms',
            STATUS_LIVE,
            detail="Africa's Talking configured",
            meta={'username': settings.AT_USERNAME},
        )
    if provider != 'dummy':
        return _entry(
            'sms',
            STATUS_CONFIGURED,
            detail=f'SMS_PROVIDER={provider!r} but credentials incomplete — using dummy fallback',
        )
    return _entry('sms', STATUS_DUMMY, detail='SMS_PROVIDER=dummy — messages logged, not delivered')


def check_tutor_provider() -> dict[str, Any]:
    from apps.tutor.providers import resolve_provider_name

    provider = resolve_provider_name()
    if provider == 'anthropic':
        return _entry(
            'ai_tutor',
            STATUS_LIVE,
            detail='Anthropic API key configured',
            meta={'provider': provider, 'model': getattr(settings, 'ANTHROPIC_MODEL', '')},
        )
    if provider == 'openai':
        return _entry(
            'ai_tutor',
            STATUS_LIVE,
            detail='OpenAI-compatible endpoint configured',
            meta={
                'provider': provider,
                'model': getattr(settings, 'OPENAI_MODEL', ''),
                'base_url': getattr(settings, 'OPENAI_BASE_URL', '') or 'https://api.openai.com/v1',
            },
        )
    return _entry(
        'ai_tutor',
        STATUS_DUMMY,
        detail='No AI provider credentials — tutor returns development stub responses',
        meta={'provider': provider, 'configured': getattr(settings, 'TUTOR_PROVIDER', 'auto')},
    )


def check_vapid() -> dict[str, Any]:
    public_key = getattr(settings, 'VAPID_PUBLIC_KEY', '') or ''
    private_key = getattr(settings, 'VAPID_PRIVATE_KEY', '') or ''
    if public_key and private_key:
        try:
            import pywebpush  # noqa: F401
        except ImportError:
            return _entry(
                'web_push',
                STATUS_CONFIGURED,
                detail='VAPID keys set but pywebpush is not installed',
            )
        return _entry('web_push', STATUS_LIVE, detail='VAPID keys configured for web push')
    if public_key or private_key:
        return _entry('web_push', STATUS_CONFIGURED, detail='VAPID key pair incomplete')
    return _entry('web_push', STATUS_UNSET, detail='VAPID keys not set — push notifications disabled')


def check_supabase() -> dict[str, Any]:
    url = getattr(settings, 'SUPABASE_URL', '') or ''
    key = getattr(settings, 'SUPABASE_KEY', '') or ''
    if url and key:
        return _entry(
            'supabase',
            STATUS_LIVE,
            detail='Supabase storage configured',
            meta={'bucket': getattr(settings, 'SUPABASE_STORAGE_BUCKET', '')},
        )
    return _entry(
        'supabase',
        STATUS_DUMMY,
        detail='Supabase unset — uploads fall back to local MEDIA_ROOT',
    )


def check_oidc() -> dict[str, Any]:
    issuer = getattr(settings, 'OIDC_ISSUER', '') or ''
    client_id = getattr(settings, 'OIDC_CLIENT_ID', '') or ''
    if issuer and client_id:
        return _entry('oidc_sso', STATUS_CONFIGURED, detail='Enterprise SSO OIDC variables present')
    if issuer or client_id:
        return _entry('oidc_sso', STATUS_CONFIGURED, detail='OIDC partially configured')
    return _entry('oidc_sso', STATUS_UNSET, detail='OIDC not configured')


def check_pypdf() -> dict[str, Any]:
    try:
        import pypdf  # noqa: F401

        return _entry('pypdf', STATUS_LIVE, detail='pypdf installed for tutor PDF retrieval')
    except ImportError:
        return _entry(
            'pypdf',
            STATUS_DEGRADED,
            detail='pypdf not installed — tutor cannot extract PDF attachment text',
        )


def collect_integration_statuses(*, include_infra: bool = True) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    if include_infra:
        checks.extend([
            check_database(),
            check_cache(),
            check_celery(),
        ])
    checks.extend([
        check_stripe(),
        check_email(),
        check_sentry(),
        check_sms(),
        check_tutor_provider(),
        check_vapid(),
        check_supabase(),
        check_oidc(),
        check_pypdf(),
    ])
    return checks


def summarize_statuses(entries: list[dict[str, Any]]) -> dict[str, Any]:
    required_missing = [
        e['name']
        for e in entries
        if e.get('required_in_production')
        and e.get('status') not in (STATUS_LIVE, STATUS_CONFIGURED, STATUS_EAGER)
    ]
    optional_dummy = [
        e['name']
        for e in entries
        if not e.get('required_in_production')
        and e.get('status') in (STATUS_DUMMY, STATUS_UNSET)
    ]
    degraded = [e['name'] for e in entries if e.get('status') == STATUS_DEGRADED]

    overall = STATUS_LIVE
    if required_missing or degraded:
        overall = STATUS_DEGRADED
    elif optional_dummy:
        overall = STATUS_CONFIGURED

    return {
        'overall': overall,
        'required_missing': required_missing,
        'degraded': degraded,
        'optional_dummy': optional_dummy,
    }


def build_integrations_report(*, include_infra: bool = True) -> dict[str, Any]:
    entries = collect_integration_statuses(include_infra=include_infra)
    summary = summarize_statuses(entries)
    return {
        'summary': summary,
        'integrations': entries,
    }
