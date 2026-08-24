"""Saved-lesson list and delete."""

from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.audit.services import log_activity
from apps.tenants.permissions import IsOrgMember

from .models import Bookmark
from .serializers import BookmarkSerializer


class BookmarkViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated, IsOrgMember]
    lookup_field = 'id'

    def get_queryset(self):
        return (
            Bookmark.objects.filter(user=self.request.user)
            .filter(
                Q(article__isnull=True) | Q(article__status='published'),
                Q(media__isnull=True) | Q(media__status='published'),
            )
            .select_related('article', 'article__category', 'media', 'media__category')
        )

    def perform_destroy(self, instance):
        bookmark_id = str(instance.id)
        kind = 'article' if instance.article_id else 'media'
        target_id = str(instance.article_id or instance.media_id)
        instance.delete()
        log_activity(
            self.request.user,
            'bookmark_removed',
            {'bookmark_id': bookmark_id, 'kind': kind, 'target_id': target_id},
            request=self.request,
        )
