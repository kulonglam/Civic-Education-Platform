from django.utils import timezone
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from apps.audit.services import log_activity
from apps.billing.services import check_quota
from apps.core.permissions import IsAdmin
from apps.core.storage import upload_file
from apps.tenants.context import get_current_organization
from apps.tenants.models import Membership
from apps.tenants.permissions import (
    CanDeleteOrgContent,
    IsOrgContentEditor,
    IsOrgMember,
    IsOrgOwnerOrAdmin,
    get_membership,
)
from apps.quizzes.models import Quiz
from apps.quizzes.serializers import QuizSerializer

from .bookmarks import BookmarkError, annotate_is_bookmarked, toggle_article_bookmark
from .models import Article, Category, MediaAsset
from .progress import record_article_progress
from .serializers import ArticleSerializer, CategorySerializer, MediaAssetSerializer

ALLOWED_ATTACHMENT_TYPES = {
    'application/pdf': '.pdf',
    'application/msword': '.doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
}
ALLOWED_IMAGE_TYPES = {
    'image/jpeg': '.jpg',
    'image/jpg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp',
    'image/gif': '.gif',
}
MAX_ATTACHMENT_BYTES = 20 * 1024 * 1024
MAX_IMAGE_BYTES = 5 * 1024 * 1024


def _can_see_unpublished(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    role = getattr(user, 'role', None)
    if role and role.name in ('editor', 'admin', 'super_admin', 'moderator'):
        return True
    membership = get_membership(user)
    return membership is not None and membership.role in (
        Membership.OWNER,
        Membership.ADMIN,
        Membership.CONTENT_MANAGER,
        Membership.MODERATOR,
    )


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Category.objects.all()

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsOrgMember(), CanDeleteOrgContent()]
        return [IsAuthenticated(), IsOrgMember(), IsOrgOwnerOrAdmin()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_locked:
            return Response(
                {'detail': 'Locked curriculum categories cannot be deleted.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


class ArticleFilter(filters.FilterSet):
    category = filters.UUIDFilter(field_name='category_id')
    tags = filters.CharFilter(method='filter_tags')
    status = filters.CharFilter()

    class Meta:
        model = Article
        fields = ['category', 'status']

    def filter_tags(self, queryset, name, value):
        return queryset.filter(tags__contains=value)


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    filterset_class = ArticleFilter
    search_fields = ['title', 'content', 'tags']
    ordering_fields = ['published_at', 'created_at', 'title']
    lookup_field = 'id'

    def get_queryset(self):
        qs = Article.objects.select_related(
            'category', 'author', 'reviewed_by', 'audio_media', 'video_media',
        ).all()
        if not _can_see_unpublished(self.request.user):
            qs = qs.filter(status='published')
        return annotate_is_bookmarked(qs, self.request.user, target='article_id')

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        if self.action in ('progress', 'bookmark'):
            return [IsAuthenticated(), IsOrgMember()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsOrgMember(), CanDeleteOrgContent()]
        if self.action in ('approve', 'reject'):
            return [IsAuthenticated(), IsOrgMember(), IsOrgOwnerOrAdmin()]
        return [IsAuthenticated(), IsOrgMember(), IsOrgContentEditor()]

    def perform_create(self, serializer):
        organization = get_current_organization()
        if organization is not None:
            check_quota(organization, 'articles')
        article = serializer.save()
        activity = 'article_submitted' if article.status == 'pending_review' else 'article_created'
        log_activity(self.request.user, activity, {'article_id': str(article.id)}, request=self.request)

    def perform_update(self, serializer):
        article = serializer.save()
        activity = 'article_submitted' if article.status == 'pending_review' else 'article_updated'
        log_activity(self.request.user, activity, {'article_id': str(article.id)}, request=self.request)

    def perform_destroy(self, instance):
        if instance.is_controlled_document:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                'Controlled documents cannot be deleted. Archive them or ask an organization owner.'
            )
        article_id = str(instance.id)
        instance.delete()
        log_activity(self.request.user, 'article_deleted', {'article_id': article_id}, request=self.request)

    @action(detail=True, methods=['post'])
    def approve(self, request, id=None):
        article = self.get_object()
        article.status = 'published'
        article.published_at = timezone.now()
        article.reviewed_by = request.user
        article.reviewed_at = timezone.now()
        article.save(update_fields=['status', 'published_at', 'reviewed_by', 'reviewed_at', 'updated_at'])
        log_activity(
            request.user,
            'article_approved',
            {'article_id': str(article.id)},
            request=request,
        )
        return Response(ArticleSerializer(article, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, id=None):
        article = self.get_object()
        article.status = 'draft'
        article.reviewed_by = request.user
        article.reviewed_at = timezone.now()
        article.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])
        log_activity(
            request.user,
            'article_rejected',
            {'article_id': str(article.id)},
            request=request,
        )
        return Response(ArticleSerializer(article, context={'request': request}).data)

    @extend_schema(
        request=inline_serializer(
            name='ArticleProgressRequest',
            fields={
                'progress_percent': serializers.IntegerField(required=False, min_value=0, max_value=100),
                'completed': serializers.BooleanField(required=False, default=False),
            },
        ),
        responses=inline_serializer(
            name='ArticleProgressResponse',
            fields={
                'progress_percent': serializers.IntegerField(),
                'completed': serializers.BooleanField(),
                'completed_at': serializers.DateTimeField(allow_null=True),
                'last_viewed_at': serializers.DateTimeField(),
            },
        ),
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOrgMember])
    def progress(self, request, id=None):
        article = self.get_object()
        progress_percent = request.data.get('progress_percent')
        completed = bool(request.data.get('completed', False))
        if progress_percent is not None:
            try:
                progress_percent = int(progress_percent)
            except (TypeError, ValueError):
                return Response(
                    {'detail': 'progress_percent must be an integer between 0 and 100.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        row = record_article_progress(
            request.user,
            article,
            progress_percent=progress_percent,
            completed=completed,
        )
        return Response({
            'progress_percent': row.progress_percent,
            'completed': row.completed,
            'completed_at': row.completed_at,
            'last_viewed_at': row.last_viewed_at,
        })

    @extend_schema(
        request=None,
        responses=inline_serializer(
            name='ArticleBookmarkToggleResponse',
            fields={'bookmarked': serializers.BooleanField()},
        ),
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOrgMember])
    def bookmark(self, request, id=None):
        article = self.get_object()
        try:
            bookmarked = toggle_article_bookmark(request.user, article)
        except BookmarkError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        log_activity(
            request.user,
            'bookmark_added' if bookmarked else 'bookmark_removed',
            {'article_id': str(article.id)},
            request=request,
        )
        return Response({'bookmarked': bookmarked})


class ArticleAttachmentUploadView(APIView):
    """Upload a PDF or document attachment for an article (e.g. full constitution text)."""

    permission_classes = [IsAuthenticated, IsOrgMember, IsOrgContentEditor]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=inline_serializer(
            name='ArticleAttachmentUploadRequest',
            fields={'file': serializers.FileField()},
        ),
        responses=inline_serializer(
            name='ArticleAttachmentUploadResponse',
            fields={
                'attachment_url': serializers.CharField(),
                'attachment_name': serializers.CharField(),
            },
        ),
    )
    def post(self, request):
        import uuid
        from pathlib import Path

        uploaded = request.FILES.get('file')
        if not uploaded:
            return Response({'detail': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        content_type = uploaded.content_type or 'application/octet-stream'
        suffix = Path(uploaded.name).suffix.lower()
        if content_type not in ALLOWED_ATTACHMENT_TYPES and suffix not in (
            '.pdf',
            '.doc',
            '.docx',
        ):
            return Response(
                {'detail': 'Only PDF and Word documents (.pdf, .doc, .docx) are allowed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if uploaded.size > MAX_ATTACHMENT_BYTES:
            return Response(
                {'detail': 'Attachment must be 20 MB or smaller.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        organization = get_current_organization()
        org_part = str(organization.id) if organization is not None else 'platform'
        ext = ALLOWED_ATTACHMENT_TYPES.get(content_type) or suffix or '.bin'
        storage_name = f'{uuid.uuid4().hex}{ext}'
        storage_path = f'articles/{org_part}/{storage_name}'

        url = upload_file(
            storage_path,
            uploaded.read(),
            content_type,
            request=request,
        )
        if not url:
            return Response(
                {'detail': 'File upload is not available. Configure Supabase storage or local media.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({
            'attachment_url': url,
            'attachment_name': uploaded.name,
        })


class ArticleImageUploadView(APIView):
    """Upload an image for featured media or inline markdown embeds."""

    permission_classes = [IsAuthenticated, IsOrgMember, IsOrgContentEditor]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=inline_serializer(
            name='ArticleImageUploadRequest',
            fields={'file': serializers.FileField()},
        ),
        responses=inline_serializer(
            name='ArticleImageUploadResponse',
            fields={
                'url': serializers.CharField(),
                'name': serializers.CharField(),
            },
        ),
    )
    def post(self, request):
        import uuid
        from pathlib import Path

        uploaded = request.FILES.get('file')
        if not uploaded:
            return Response({'detail': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        content_type = uploaded.content_type or 'application/octet-stream'
        suffix = Path(uploaded.name).suffix.lower()
        if content_type not in ALLOWED_IMAGE_TYPES and suffix not in (
            '.jpg',
            '.jpeg',
            '.png',
            '.webp',
            '.gif',
        ):
            return Response(
                {'detail': 'Only JPEG, PNG, WebP, or GIF images are allowed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if uploaded.size > MAX_IMAGE_BYTES:
            return Response(
                {'detail': 'Image must be 5 MB or smaller.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        organization = get_current_organization()
        org_part = str(organization.id) if organization is not None else 'platform'
        ext = ALLOWED_IMAGE_TYPES.get(content_type) or suffix or '.jpg'
        storage_name = f'{uuid.uuid4().hex}{ext}'
        storage_path = f'articles/{org_part}/images/{storage_name}'

        url = upload_file(
            storage_path,
            uploaded.read(),
            content_type,
            request=request,
        )
        if not url:
            return Response(
                {'detail': 'File upload is not available. Configure Supabase storage or local media.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({
            'url': url,
            'name': uploaded.name,
        })


class ContentBundleThrottle(UserRateThrottle):
    scope = 'content_bundle'


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsOrgMember])
def content_bundle(request):
    """Download a full offline study pack for the current organisation.

    Returns all published articles and their associated quizzes in a single
    JSON payload optimised for bulk offline caching.  Rate-limited to
    4 downloads per hour per user to keep bandwidth reasonable.

    GET /api/v1/content-bundle/
    Optional query params:
      - category_id: restrict to a single category
    """
    throttle = ContentBundleThrottle()
    if not throttle.allow_request(request, None):
        from rest_framework.exceptions import Throttled
        raise Throttled(detail='Content bundle rate limit exceeded. Try again in an hour.')

    qs = Article.objects.filter(status='published').select_related(
        'category', 'author', 'audio_media', 'video_media',
    )
    category_id = request.query_params.get('category_id')
    if category_id:
        qs = qs.filter(category_id=category_id)

    articles_data = ArticleSerializer(qs, many=True, context={'request': request}).data

    # Quizzes are org-scoped (no category FK). Include active quizzes for offline study.
    quizzes_qs = Quiz.objects.filter(is_active=True).prefetch_related('questions')
    quizzes_data = QuizSerializer(quizzes_qs, many=True, context={'request': request}).data

    media_qs = MediaAsset.objects.filter(status='published').select_related('category', 'author')
    if category_id:
        media_qs = media_qs.filter(category_id=category_id)
    media_data = MediaAssetSerializer(media_qs, many=True, context={'request': request}).data

    if category_id:
        categories_qs = Category.objects.filter(id=category_id)
    else:
        categories_qs = Category.objects.filter(
            id__in=qs.values_list('category_id', flat=True).distinct()
        )
    categories_data = CategorySerializer(categories_qs, many=True, context={'request': request}).data

    return Response({
        'version': 1,
        'generated_at': timezone.now().isoformat(),
        'categories': categories_data,
        'articles': articles_data,
        'quizzes': quizzes_data,
        'media': media_data,
    })
