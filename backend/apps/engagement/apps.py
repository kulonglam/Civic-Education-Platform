from django.apps import AppConfig


class EngagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.engagement'
    label = 'engagement'

    def ready(self):
        import apps.engagement.signals  # noqa: F401
