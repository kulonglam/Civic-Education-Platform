from django.urls import path

from .views import HealthCheckView, ReadinessCheckView, SecurityEventListView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('ready/', ReadinessCheckView.as_view(), name='readiness-check'),
    path('security/events/', SecurityEventListView.as_view(), name='security-events'),
]
