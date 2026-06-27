from django.urls import include, path
from rest_framework.routers import DefaultRouter

from ..views import ArticleAttachmentUploadView, ArticleViewSet

router = DefaultRouter()
router.register('', ArticleViewSet, basename='article')

urlpatterns = [
    path('attachments/upload/', ArticleAttachmentUploadView.as_view(), name='article-attachment-upload'),
    path('', include(router.urls)),
]
