from django.urls import path

from .views import (
    HealthCheckView,
    IntegrationsStatusView,
    PublicConfigView,
    ReadinessCheckView,
    SecurityEventListView,
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('branding/', PublicConfigView.as_view(), name='public-branding'),
    path('ready/', ReadinessCheckView.as_view(), name='readiness-check'),
    path('integrations/status/', IntegrationsStatusView.as_view(), name='integrations-status'),
    path('security/events/', SecurityEventListView.as_view(), name='security-events'),
]
