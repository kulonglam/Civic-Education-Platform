from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .event_views import CivicEventViewSet

router = DefaultRouter()
router.register('', CivicEventViewSet, basename='civic-events')

urlpatterns = [
    path('', include(router.urls)),
]
