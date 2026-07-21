from django.urls import include, path
from rest_framework.routers import DefaultRouter

from ..media_views import MediaAssetViewSet, MediaAudioUploadView, MediaVideoUploadView

router = DefaultRouter()
router.register('', MediaAssetViewSet, basename='media')

urlpatterns = [
    path('audio/upload/', MediaAudioUploadView.as_view(), name='media-audio-upload'),
    path('video/upload/', MediaVideoUploadView.as_view(), name='media-video-upload'),
    path('', include(router.urls)),
]
