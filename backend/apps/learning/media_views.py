"""Media library API: CRUD + audio/video uploads."""

from pathlib import Path

from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import log_activity
from apps.core.storage import upload_file
from apps.tenants.context import get_current_organization
from apps.tenants.models import Membership
from apps.tenants.permissions import (
    CanDeleteOrgContent,
    IsOrgContentEditor,
    IsOrgMember,
    get_membership,
)

from .models import MediaAsset
from .progress import record_media_progress
from .serializers import MediaAssetSerializer

ALLOWED_AUDIO_TYPES = {
    'audio/mpeg': '.mp3',
    'audio/mp3': '.mp3',
    'audio/mp4': '.m4a',
    'audio/x-m4a': '.m4a',
    'audio/ogg': '.ogg',
    'audio/wav': '.wav',
    'audio/x-wav': '.wav',
    'audio/webm': '.webm',
}
ALLOWED_VIDEO_TYPES = {
    'video/mp4': '.mp4',
    'video/webm': '.webm',
}
MAX_AUDIO_BYTES = 30 * 1024 * 1024
MAX_VIDEO_BYTES = 100 * 1024 * 1024


def _can_see_unpublished(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    role = getattr(user, 'role', None)
    if role and role.name in ('editor', 'admin', 'moderator'):
        return True
    membership = get_membership(user)
    return membership is not None and membership.role in (
        Membership.OWNER,
        Membership.ADMIN,
        Membership.CONTENT_MANAGER,
        Membership.MODERATOR,
    )


class MediaAssetFilter(filters.FilterSet):
    category = filters.UUIDFilter(field_name='category_id')
    media_type = filters.CharFilter()
    status = filters.CharFilter()

    class Meta:
        model = MediaAsset
        fields = ['category', 'media_type', 'status']


class MediaAssetViewSet(viewsets.ModelViewSet):
    serializer_class = MediaAssetSerializer
    filterset_class = MediaAssetFilter
    search_fields = ['title', 'title_ar', 'description']
    ordering_fields = ['published_at', 'created_at', 'title']
    lookup_field = 'id'

    def get_queryset(self):
        qs = MediaAsset.objects.select_related('category', 'author').all()
        if not _can_see_unpublished(self.request.user):
            qs = qs.filter(status='published')
        return qs

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        if self.action == 'progress':
            return [IsAuthenticated(), IsOrgMember()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsOrgMember(), CanDeleteOrgContent()]
        return [IsAuthenticated(), IsOrgMember(), IsOrgContentEditor()]

    def perform_create(self, serializer):
        asset = serializer.save()
        log_activity(
            self.request.user,
            'media_created',
            {'media_id': str(asset.id), 'media_type': asset.media_type},
            request=self.request,
        )

    def perform_update(self, serializer):
        asset = serializer.save()
        log_activity(
            self.request.user,
            'media_updated',
            {'media_id': str(asset.id), 'media_type': asset.media_type},
            request=self.request,
        )

    def perform_destroy(self, instance):
        media_id = str(instance.id)
        media_type = instance.media_type
        instance.delete()
        log_activity(
            self.request.user,
            'media_deleted',
            {'media_id': media_id, 'media_type': media_type},
            request=self.request,
        )

    @extend_schema(
        request=inline_serializer(
            name='MediaProgressRequest',
            fields={'completed': serializers.BooleanField(required=False, default=False)},
        ),
        responses=inline_serializer(
            name='MediaProgressResponse',
            fields={
                'completed': serializers.BooleanField(),
                'completed_at': serializers.DateTimeField(allow_null=True),
                'last_viewed_at': serializers.DateTimeField(),
            },
        ),
    )
    @action(detail=True, methods=['post'])
    def progress(self, request, id=None):
        media = self.get_object()
        completed = bool(request.data.get('completed', False))
        row = record_media_progress(request.user, media, completed=completed)
        return Response({
            'completed': row.completed,
            'completed_at': row.completed_at,
            'last_viewed_at': row.last_viewed_at,
        })


def _upload_media_file(
    request,
    *,
    allowed_types: dict,
    allowed_suffixes: tuple,
    max_bytes: int,
    storage_subdir: str,
    type_label: str,
):
    import uuid

    uploaded = request.FILES.get('file')
    if not uploaded:
        return Response({'detail': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

    content_type = uploaded.content_type or 'application/octet-stream'
    suffix = Path(uploaded.name).suffix.lower()
    if content_type not in allowed_types and suffix not in allowed_suffixes:
        return Response(
            {'detail': f'Only {type_label} files are allowed.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if uploaded.size > max_bytes:
        mb = max_bytes // (1024 * 1024)
        return Response(
            {'detail': f'File must be {mb} MB or smaller.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    organization = get_current_organization()
    org_part = str(organization.id) if organization is not None else 'platform'
    ext = allowed_types.get(content_type) or suffix or '.bin'
    storage_name = f'{uuid.uuid4().hex}{ext}'
    storage_path = f'media/{org_part}/{storage_subdir}/{storage_name}'

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
        'mime_type': content_type,
        'source': MediaAsset.SOURCE_UPLOAD,
    })


class MediaAudioUploadView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember, IsOrgContentEditor]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=inline_serializer(
            name='MediaAudioUploadRequest',
            fields={'file': serializers.FileField()},
        ),
        responses=inline_serializer(
            name='MediaAudioUploadResponse',
            fields={
                'url': serializers.CharField(),
                'name': serializers.CharField(),
                'mime_type': serializers.CharField(),
                'source': serializers.CharField(),
            },
        ),
    )
    def post(self, request):
        return _upload_media_file(
            request,
            allowed_types=ALLOWED_AUDIO_TYPES,
            allowed_suffixes=('.mp3', '.m4a', '.ogg', '.wav', '.webm'),
            max_bytes=MAX_AUDIO_BYTES,
            storage_subdir='audio',
            type_label='audio (mp3, m4a, ogg, wav)',
        )


class MediaVideoUploadView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember, IsOrgContentEditor]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=inline_serializer(
            name='MediaVideoUploadRequest',
            fields={'file': serializers.FileField()},
        ),
        responses=inline_serializer(
            name='MediaVideoUploadResponse',
            fields={
                'url': serializers.CharField(),
                'name': serializers.CharField(),
                'mime_type': serializers.CharField(),
                'source': serializers.CharField(),
            },
        ),
    )
    def post(self, request):
        return _upload_media_file(
            request,
            allowed_types=ALLOWED_VIDEO_TYPES,
            allowed_suffixes=('.mp4', '.webm'),
            max_bytes=MAX_VIDEO_BYTES,
            storage_subdir='video',
            type_label='video (mp4, webm)',
        )
