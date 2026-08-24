from django.urls import include, path
from rest_framework.routers import DefaultRouter

from ..bookmark_views import BookmarkViewSet

router = DefaultRouter()
router.register('', BookmarkViewSet, basename='bookmark')

urlpatterns = [
    path('', include(router.urls)),
]
