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

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

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
    },
}
