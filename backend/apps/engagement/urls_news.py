from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .news_views import CivicNewsViewSet

router = DefaultRouter()
router.register('', CivicNewsViewSet, basename='civic-news')

urlpatterns = [
    path('', include(router.urls)),
]
