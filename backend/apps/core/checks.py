from django.conf import settings
from django.core.checks import Error, Warning, register


@register(deploy=True)
def production_security_checks(app_configs, **kwargs):
    """Validate settings required for a safe production deployment."""
    if settings.DEBUG:
        return []

    errors: list[Error] = []
    warnings: list[Warning] = []

    secret = getattr(settings, 'SECRET_KEY', '')
    if not secret or secret.startswith('django-insecure') or secret.startswith('change-me'):
        errors.append(
            Error(
                'SECRET_KEY must be a unique random value in production.',
                id='core.E001',
            )
        )

    allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
    if not allowed_hosts:
        errors.append(
            Error(
                'ALLOWED_HOSTS must list your API domain(s) in production.',
                id='core.E002',
            )
        )

    cors_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
    if not cors_origins:
        errors.append(
            Error(
                'CORS_ALLOWED_ORIGINS must list your frontend URL(s) in production.',
                id='core.E003',
            )
        )

    if getattr(settings, 'BILLING_PROVIDER', 'dummy') == 'dummy':
        allow_dummy = getattr(settings, 'ALLOW_DUMMY_BILLING_IN_PRODUCTION', False)
        if not allow_dummy:
            try:
                from decouple import config

                allow_dummy = config('ALLOW_DUMMY_BILLING_IN_PRODUCTION', default=False, cast=bool)
            except Exception:  # noqa: BLE001
                pass
        if not allow_dummy:
            errors.append(
                Error(
                    'BILLING_PROVIDER must be "stripe" in production, or set '
                    'ALLOW_DUMMY_BILLING_IN_PRODUCTION=True when payments are not used.',
                    id='core.E004',
                )
            )

    if not getattr(settings, 'CELERY_BROKER_URL', ''):
        errors.append(
            Error(
                'CELERY_BROKER_URL is required in production for background tasks.',
                id='core.E005',
            )
        )

    if getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', True):
        errors.append(
            Error(
                'CELERY_TASK_ALWAYS_EAGER must be False in production.',
                id='core.E006',
            )
        )

    frontend_url = getattr(settings, 'FRONTEND_URL', '')
    if frontend_url and not frontend_url.startswith('https://'):
        warnings.append(
            Warning(
                'FRONTEND_URL should use HTTPS in production.',
                id='core.W001',
            )
        )

    if getattr(settings, 'BILLING_PROVIDER', '') == 'stripe':
        if not getattr(settings, 'STRIPE_SECRET_KEY', ''):
            errors.append(
                Error(
                    'STRIPE_SECRET_KEY is required when BILLING_PROVIDER=stripe.',
                    id='core.E007',
                )
            )
        if not getattr(settings, 'STRIPE_WEBHOOK_SECRET', ''):
            errors.append(
                Error(
                    'STRIPE_WEBHOOK_SECRET is required when BILLING_PROVIDER=stripe.',
                    id='core.E008',
                )
            )

    if not getattr(settings, 'EMAIL_HOST', ''):
        errors.append(
            Error(
                'EMAIL_HOST is required in production for verification and password reset.',
                id='core.E009',
            )
        )

    require_sentry = True
    try:
        from decouple import config

        require_sentry = config('REQUIRE_SENTRY', default=True, cast=bool)
    except Exception:  # noqa: BLE001
        pass
    if require_sentry and not getattr(settings, 'SENTRY_DSN', ''):
        errors.append(
            Error(
                'SENTRY_DSN is required in production (set REQUIRE_SENTRY=False only for staging).',
                id='core.E010',
            )
        )

    return errors + warnings
