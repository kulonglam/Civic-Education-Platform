from datetime import timedelta
from pathlib import Path

import dj_database_url
from celery.schedules import crontab
from decouple import config

from apps.core.branding import PLATFORM_NAME, PLATFORM_NAME_API

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

def _optional_app(app_name):
    try:
        import importlib
        importlib.import_module(app_name.replace('.apps.', '.').split('.')[0])
        return [app_name]
    except ImportError:
        return []


INSTALLED_APPS = [
    *_optional_app('daphne'),
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    *_optional_app('channels'),
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    # Local apps
    'apps.core',
    'apps.tenants',
    'apps.billing',
    'apps.accounts',
    'apps.learning',
    'apps.quizzes',
    'apps.forum',
    'apps.notifications',
    'apps.analytics',
    'apps.audit',
    'apps.tutor',
    'apps.gamification',
    'apps.engagement',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'apps.core.middleware.ContentSecurityPolicyMiddleware',
    'apps.core.middleware.SecurityHeadersMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.tenants.middleware.TenantMiddleware',
    'apps.core.middleware.IpAllowlistMiddleware',
    'apps.core.middleware.SetJWTCookieMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=config(
            'DATABASE_URL',
            default='postgres://postgres:postgres@localhost:5432/civic_education',
        ),
        conn_max_age=600,
    )
}

# Optional read replica — set DATABASE_URL_REPLICA to enable.
_DATABASE_URL_REPLICA = config('DATABASE_URL_REPLICA', default='')
if _DATABASE_URL_REPLICA:
    DATABASES['replica'] = dj_database_url.config(
        default=_DATABASE_URL_REPLICA,
        conn_max_age=600,
    )
    DATABASE_ROUTERS = ['apps.core.db.ReadReplicaRouter']

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Juba'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    # CompressedStaticFilesStorage (not Manifest) — Manifest raises 500s when
    # collectstatic is incomplete (e.g. Docker build with || true) or when the
    # browsable API asks for DRF CSS that is missing from the hash map.
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.accounts.authentication.JWTCookieAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1'],
    'VERSION_PARAM': 'version',
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/min',
        'user': '100/min',
        'auth': '5/min',
        'ai_tutor': '10/min',
        'content_bundle': '4/hour',
        'awareness_report': '8/hour',
        'forum_report': '8/hour',
    },
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=config('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=15, cast=int)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

SPECTACULAR_SETTINGS = {
    'TITLE': PLATFORM_NAME_API,
    'DESCRIPTION': 'REST API for civic education, quizzes, forum, and analytics.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

CORS_ALLOW_CREDENTIALS = True

FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:5173')
API_BASE_URL = config('API_BASE_URL', default='http://127.0.0.1:8000')
SUPPORT_EMAIL = config('SUPPORT_EMAIL', default='')

# Enterprise SSO (OpenID Connect)
OIDC_ISSUER = config('OIDC_ISSUER', default='')
OIDC_CLIENT_ID = config('OIDC_CLIENT_ID', default='')
OIDC_CLIENT_SECRET = config('OIDC_CLIENT_SECRET', default='')
OIDC_REDIRECT_URI = config('OIDC_REDIRECT_URI', default='')
OIDC_SCOPES = config('OIDC_SCOPES', default='openid email profile')

# Default workspace for individual citizen sign-ups (seed_data creates platform-demo).
PUBLIC_ORGANIZATION_SLUG = config('PUBLIC_ORGANIZATION_SLUG', default='platform-demo')

SUPABASE_URL = config('SUPABASE_URL', default='')
SUPABASE_KEY = config('SUPABASE_KEY', default='')
SUPABASE_STORAGE_BUCKET = config('SUPABASE_STORAGE_BUCKET', default='civic-platform')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@civic-education.ss')

# Celery
# In development the broker is optional: tasks run eagerly (synchronously, inline)
# unless a broker is configured and CELERY_TASK_ALWAYS_EAGER is set to False.
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='')
CELERY_TASK_ALWAYS_EAGER = config('CELERY_TASK_ALWAYS_EAGER', default=DEBUG, cast=bool)
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BEAT_SCHEDULE = {
    'send-due-event-reminders': {
        'task': 'apps.engagement.tasks.send_due_event_reminders',
        'schedule': crontab(minute='*/15'),
    },
}

# Billing
# 'dummy' (default) needs no external service; checkout activates instantly.
# 'stripe' integrates Stripe Checkout + Billing Portal (requires keys below).
BILLING_PROVIDER = config('BILLING_PROVIDER', default='dummy')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')
STRIPE_PRICE_IDS = {
    'pro': config('STRIPE_PRICE_PRO', default=''),
    'enterprise': config('STRIPE_PRICE_ENTERPRISE', default=''),
}
AUDIT_WORM_PATH = config('AUDIT_WORM_PATH', default='')

# AI Tutor
# 'auto' (default) picks Anthropic, then OpenAI-compatible, then the offline stub,
# based on which credentials are present. Force one with 'anthropic', 'openai' or 'stub'.
TUTOR_PROVIDER = config('TUTOR_PROVIDER', default='auto')

ANTHROPIC_API_KEY = config('ANTHROPIC_API_KEY', default='')
ANTHROPIC_MODEL = config('ANTHROPIC_MODEL', default='claude-sonnet-4-20250514')
ANTHROPIC_MAX_TOKENS = config('ANTHROPIC_MAX_TOKENS', default=1024, cast=int)

# Any OpenAI-compatible endpoint. Leave OPENAI_BASE_URL blank for OpenAI itself, or
# point it at a free local runtime (Ollama: http://localhost:11434/v1) or a gateway.
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
OPENAI_BASE_URL = config('OPENAI_BASE_URL', default='')
OPENAI_MODEL = config('OPENAI_MODEL', default='gpt-4o-mini')
OPENAI_MAX_TOKENS = config('OPENAI_MAX_TOKENS', default=1024, cast=int)

# Article auto-translation (reuses TUTOR_PROVIDER). Stub provider never writes into articles.
TRANSLATION_ENABLED = config('TRANSLATION_ENABLED', default=True, cast=bool)
TRANSLATION_MAX_TOKENS = config('TRANSLATION_MAX_TOKENS', default=4096, cast=int)
TRANSLATION_CHUNK_CHARS = config('TRANSLATION_CHUNK_CHARS', default=3000, cast=int)

def _env_first(*names: str) -> str:
    for name in names:
        value = config(name, default='')
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ''


# Brevo REST API (port 443). Distinct from the SMTP key (xsmtpsib-…).
BREVO_API_KEY = _env_first('BREVO_API_KEY', 'SENDINBLUE_API_KEY')

# SMS (Africa's Talking). AFRICASTALKING_* aliases match the dashboard copy.
SMS_PROVIDER = config('SMS_PROVIDER', default='dummy')
AT_USERNAME = _env_first('AT_USERNAME', 'AFRICASTALKING_USERNAME')
AT_API_KEY = _env_first('AT_API_KEY', 'AFRICASTALKING_API_KEY')
AT_SENDER_ID = _env_first('AT_SENDER_ID', 'AFRICASTALKING_SENDER_ID')
if AT_USERNAME and AT_API_KEY and SMS_PROVIDER == 'dummy':
    SMS_PROVIDER = 'africastalking'
# Production sets this True so dummy SMS cannot pretend an OTP was delivered.
REQUIRE_LIVE_SMS = False

# WhatsApp Cloud API (optional — dummy logger when unset)
WHATSAPP_PROVIDER = config('WHATSAPP_PROVIDER', default='dummy')
WHATSAPP_ACCESS_TOKEN = config('WHATSAPP_ACCESS_TOKEN', default='')
WHATSAPP_PHONE_NUMBER_ID = config('WHATSAPP_PHONE_NUMBER_ID', default='')
WHATSAPP_VERIFY_TOKEN = config('WHATSAPP_VERIFY_TOKEN', default='')
WHATSAPP_APP_SECRET = config('WHATSAPP_APP_SECRET', default='')
WHATSAPP_DISPLAY_NUMBER = config('WHATSAPP_DISPLAY_NUMBER', default='')
# Approved Meta template for business-initiated alerts ({{1}} = message body).
WHATSAPP_TEMPLATE_NAME = config('WHATSAPP_TEMPLATE_NAME', default='')
WHATSAPP_TEMPLATE_LANG = config('WHATSAPP_TEMPLATE_LANG', default='en')
WHATSAPP_TEMPLATE_BODY_VARS = config('WHATSAPP_TEMPLATE_BODY_VARS', default=1, cast=int)

# Web Push (optional — generate VAPID keys for browser notifications)
VAPID_PUBLIC_KEY = config('VAPID_PUBLIC_KEY', default='')
VAPID_PRIVATE_KEY = config('VAPID_PRIVATE_KEY', default='')
VAPID_ADMIN_EMAIL = config('VAPID_ADMIN_EMAIL', default='mailto:admin@civic-education.ss')

# Cache (Redis in prod; locmem fallback locally)
REDIS_URL = config('REDIS_URL', default='')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# ── Django Channels ───────────────────────────────────────────────────────────
ASGI_APPLICATION = 'config.asgi.application'
if REDIS_URL:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {'hosts': [REDIS_URL]},
        }
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        }
    }

# Logging: structured, level-controlled, with explicit app loggers.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': config('LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'apps': {
            'handlers': ['console'],
            'level': config('APP_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

MFA_ISSUER_NAME = config('MFA_ISSUER_NAME', default=PLATFORM_NAME)

# Privileged-role idle timeout (seconds). Enforced server-side via cache.
SESSION_IDLE_TIMEOUT_SECONDS = config('SESSION_IDLE_TIMEOUT_SECONDS', default=30 * 60, cast=int)

# ── JWT Cookie settings ──────────────────────────────────────────────────────
JWT_ACCESS_COOKIE = 'cep_access'
JWT_REFRESH_COOKIE = 'cep_refresh'
JWT_COOKIE_SAMESITE = config('JWT_COOKIE_SAMESITE', default='Lax')
JWT_COOKIE_SECURE = config('JWT_COOKIE_SECURE', default=not DEBUG, cast=bool)
JWT_COOKIE_HTTPONLY = True

# ── Content Security Policy ───────────────────────────────────────────────────
# unsafe-inline kept for Vite/React style injection; unsafe-eval removed.
# jsdelivr: drf-spectacular Swagger UI loads swagger-ui-dist from CDN by default.
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net")
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    "https://fonts.googleapis.com",
    "https://cdn.jsdelivr.net",
)
CSP_FONT_SRC = ("'self'", "data:", "https://fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:", "https:", "blob:")
CSP_CONNECT_SRC = ("'self'", config('FRONTEND_URL', default='http://localhost:5173'), "wss:")
CSP_OBJECT_SRC = ("'none'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_UPGRADE_INSECURE_REQUESTS = not DEBUG

# Optional error tracking. No-op unless SENTRY_DSN is set and sentry-sdk is installed.
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.django import DjangoIntegration

        integrations = [DjangoIntegration(), CeleryIntegration()]
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=integrations,
            traces_sample_rate=config('SENTRY_TRACES_SAMPLE_RATE', default=0.0, cast=float),
            send_default_pii=False,
            environment=config('SENTRY_ENVIRONMENT', default='production'),
        )
    except ImportError:
        pass
