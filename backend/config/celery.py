import os

from celery import Celery

# Guard: require an explicit DJANGO_SETTINGS_MODULE so Celery workers
# do not accidentally boot with development settings in a production deploy.
# Set DJANGO_SETTINGS_MODULE=config.settings.production in your environment.
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    raise RuntimeError(
        'DJANGO_SETTINGS_MODULE is not set. '
        'Export it before starting Celery (e.g. config.settings.production).'
    )

app = Celery('civic_education')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
