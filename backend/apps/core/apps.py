from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    label = 'core'

    def ready(self):
        from django.conf import settings
        from django.contrib import admin

        from . import checks  # noqa: F401

        frontend = (getattr(settings, 'FRONTEND_URL', '') or '').rstrip('/')
        if frontend:
            admin.site.site_url = frontend
