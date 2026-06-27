from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from apps.audit.services import log_activity
from apps.billing.services import check_quota
from apps.core.permissions import IsAdmin, IsEditorOrAdmin
from apps.core.storage import upload_file
from apps.tenants.context import get_current_organization
from apps.tenants.permissions import IsOrgMember, IsOrgOwnerOrAdmin
from apps.quizzes.models import Quiz
from apps.quizzes.serializers import QuizSerializer

from .models import Article, Category
from .serializers import ArticleSerializer, CategorySerializer

ALLOWED_ATTACHMENT_TYPES = {
    'application/pdf': '.pdf',
    'application/msword': '.doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
}
MAX_ATTACHMENT_BYTES = 20 * 1024 * 1024


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated(), IsOrgMember(), IsOrgOwnerOrAdmin()]


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
        qs = Article.objects.select_related('category', 'author').all()
        user = self.request.user
        if not user.is_authenticated or user.role.name not in ('editor', 'admin'):
            qs = qs.filter(status='published')
        return qs

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsOrgMember(), IsAdmin()]
        return [IsAuthenticated(), IsOrgMember(), IsEditorOrAdmin()]

    def perform_create(self, serializer):
        organization = get_current_organization()
        if organization is not None:
            check_quota(organization, 'articles')
        article = serializer.save()
        log_activity(self.request.user, 'article_created', {'article_id': str(article.id)})

    def perform_update(self, serializer):
        article = serializer.save()
        log_activity(self.request.user, 'article_updated', {'article_id': str(article.id)})

    def perform_destroy(self, instance):
        article_id = str(instance.id)
        instance.delete()
        log_activity(self.request.user, 'article_deleted', {'article_id': article_id})


class ArticleAttachmentUploadView(APIView):
    """Upload a PDF or document attachment for an article (e.g. full constitution text)."""

    permission_classes = [IsAuthenticated, IsOrgMember, IsEditorOrAdmin]
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


class ContentBundleThrottle(UserRateThrottle):
    rate = '4/hour'
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

    qs = Article.objects.filter(status='published').select_related('category', 'author')
    category_id = request.query_params.get('category_id')
    if category_id:
        qs = qs.filter(category_id=category_id)

    articles_data = ArticleSerializer(qs, many=True, context={'request': request}).data

    # Fetch quizzes associated with the same categories as the articles
    cat_ids = qs.values_list('category_id', flat=True).distinct()
    quizzes_qs = Quiz.objects.filter(category_id__in=cat_ids).prefetch_related('questions__choices')
    quizzes_data = QuizSerializer(quizzes_qs, many=True, context={'request': request}).data

    categories_qs = Category.objects.filter(id__in=cat_ids)
    categories_data = CategorySerializer(categories_qs, many=True, context={'request': request}).data

    return Response({
        'version': 1,
        'generated_at': __import__('django.utils.timezone', fromlist=['timezone']).timezone.now().isoformat(),
        'categories': categories_data,
        'articles': articles_data,
        'quizzes': quizzes_data,
    })
