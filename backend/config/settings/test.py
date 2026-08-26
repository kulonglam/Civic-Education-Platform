from .base import *  # noqa: F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
BREVO_API_KEY = ''
DEBUG = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Never call a live SMS provider from pytest even if .env has Africa's Talking keys.
SMS_PROVIDER = 'dummy'
AT_USERNAME = ''
AT_API_KEY = ''
AT_SENDER_ID = ''
REQUIRE_LIVE_SMS = False

# Disable rate limiting in tests so repeated auth calls don't trip the throttle.
# Auth views use AuthRateThrottle (scope=auth); keep rates effectively unlimited.
# Note: pytest must use --ds=config.settings.test so .env DJANGO_SETTINGS_MODULE
# (development) does not win over pytest.ini and re-enable 5/min auth limits.
REST_FRAMEWORK = {  # noqa: F405
    **REST_FRAMEWORK,  # noqa: F405
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {
        'auth': '10000/min',
        'anon': '10000/min',
        'user': '10000/min',
        'ai_tutor': '10000/min',
        'content_bundle': '10000/min',
        'awareness_report': '10000/min',
        'forum_report': '10000/min',
    },
}
