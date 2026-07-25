from django.utils import timezone
from rest_framework import serializers

from apps.core.sanitize import reject_dangerous_markdown
from apps.core.utils import get_preferred_language
from apps.tenants.context import get_current_organization
from apps.tenants.models import Membership
from apps.tenants.permissions import get_membership

from .models import Article, Category, MediaAsset


def validate_http_url(value: str, *, field_name: str = 'URL') -> str:
    if not value:
        return value
    value = value.strip()
    if not value.startswith(('http://', 'https://')):
        raise serializers.ValidationError(f'{field_name} must use http or https.')
    return value


def _can_publish_directly(request) -> bool:
    user = request.user
    if not user or not user.is_authenticated:
        return False
    if getattr(user, 'role', None) and user.role.name == 'admin':
        return True
    membership = get_membership(user)
    return membership is not None and membership.role in (Membership.OWNER, Membership.ADMIN)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'name_ar', 'description_ar', 'is_locked',
        ]

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        if instance and instance.is_locked:
            request = self.context.get('request')
            user = getattr(request, 'user', None) if request else None
            membership = get_membership(user) if user else None
            is_owner_admin = membership and membership.role in (
                Membership.OWNER,
                Membership.ADMIN,
            )
            platform_admin = (
                user
                and getattr(user, 'role', None)
                and user.role.name == 'admin'
            )
            if not (is_owner_admin or platform_admin):
                for field in ('name', 'slug'):
                    if field in attrs and attrs[field] != getattr(instance, field):
                        raise serializers.ValidationError(
                            {field: 'Locked curriculum categories cannot rename name/slug.'}
                        )
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and get_preferred_language(request) == 'ar':
            if data.get('name_ar'):
                data['name'] = data['name_ar']
            if data.get('description_ar'):
                data['description'] = data['description_ar']
        return data


class MediaAssetSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    author_name = serializers.CharField(source='author.full_name', read_only=True, default=None)
    playback_url = serializers.CharField(read_only=True)

    class Meta:
        model = MediaAsset
        fields = [
            'id', 'title', 'title_ar', 'description', 'description_ar',
            'media_type', 'source', 'file_url', 'external_url', 'playback_url',
            'mime_type', 'duration_seconds', 'thumbnail_url', 'captions_url',
            'category', 'category_id', 'status',
            'author', 'author_name', 'published_at', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'author', 'published_at', 'created_at', 'updated_at', 'playback_url',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and get_preferred_language(request) == 'ar':
            if data.get('title_ar'):
                data['title'] = data['title_ar']
            if data.get('description_ar'):
                data['description'] = data['description_ar']
        data['playback_url'] = instance.playback_url
        return data

    def validate_category_id(self, value):
        if value is None:
            return value
        organization = get_current_organization()
        qs = Category.objects.filter(id=value)
        if organization is not None:
            qs = qs.filter(organization=organization)
        if not qs.exists():
            raise serializers.ValidationError(
                'Category not found or does not belong to your organisation.'
            )
        return value

    def validate_external_url(self, value):
        return validate_http_url(value, field_name='External URL')

    def validate_file_url(self, value):
        if not value:
            return value
        value = value.strip()
        if value.startswith(('http://', 'https://', '/')):
            return value
        raise serializers.ValidationError('File URL must be an absolute http(s) URL or media path.')

    def validate_thumbnail_url(self, value):
        return validate_http_url(value, field_name='Thumbnail URL')

    def validate_captions_url(self, value):
        return validate_http_url(value, field_name='Captions URL')

    def validate(self, attrs):
        source = attrs.get('source', getattr(self.instance, 'source', MediaAsset.SOURCE_EXTERNAL))
        file_url = attrs.get(
            'file_url',
            getattr(self.instance, 'file_url', '') if self.instance else '',
        )
        external_url = attrs.get(
            'external_url',
            getattr(self.instance, 'external_url', '') if self.instance else '',
        )
        errors = {}
        if source == MediaAsset.SOURCE_UPLOAD and not (file_url or '').strip():
            errors['file_url'] = 'File URL is required for uploaded media.'
        if source == MediaAsset.SOURCE_EXTERNAL and not (external_url or '').strip():
            errors['external_url'] = 'External URL is required for external media.'
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def _normalize_publish_status(self, validated_data):
        if validated_data.get('status') == 'published':
            validated_data['published_at'] = timezone.now()
        return validated_data

    def create(self, validated_data):
        category_id = validated_data.pop('category_id', serializers.empty)
        if category_id is not serializers.empty:
            validated_data['category_id'] = category_id
        validated_data['author'] = self.context['request'].user
        validated_data = self._normalize_publish_status(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'category_id' in validated_data:
            validated_data['category_id'] = validated_data.pop('category_id')
        validated_data = self._normalize_publish_status(validated_data)
        return super().update(instance, validated_data)


class MediaAssetSummarySerializer(serializers.ModelSerializer):
    """Compact nested representation for articles."""

    playback_url = serializers.CharField(read_only=True)

    class Meta:
        model = MediaAsset
        fields = [
            'id', 'title', 'title_ar', 'media_type', 'source',
            'file_url', 'external_url', 'playback_url', 'mime_type',
            'duration_seconds', 'thumbnail_url', 'captions_url', 'status',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and get_preferred_language(request) == 'ar' and data.get('title_ar'):
            data['title'] = data['title_ar']
        data['playback_url'] = instance.playback_url
        return data


class ArticleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True)
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    reviewed_by_name = serializers.CharField(
        source='reviewed_by.full_name', read_only=True, default=None, allow_null=True,
    )
    audio_media = MediaAssetSummarySerializer(read_only=True)
    video_media = MediaAssetSummarySerializer(read_only=True)
    audio_media_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    video_media_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'title_ar', 'content', 'content_ar',
            'category', 'category_id', 'author', 'author_name',
            'tags', 'featured_image_url', 'attachment_url', 'attachment_name',
            'attachment_version', 'document_label', 'is_controlled_document',
            'audio_media', 'audio_media_id', 'video_media', 'video_media_id',
            'status', 'reviewed_by', 'reviewed_by_name',
            'reviewed_at', 'published_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'author', 'published_at', 'reviewed_by', 'reviewed_at',
            'created_at', 'updated_at',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and get_preferred_language(request) == 'ar':
            if data.get('title_ar'):
                data['title'] = data['title_ar']
            if data.get('content_ar'):
                data['content'] = data['content_ar']
        return data

    def validate_category_id(self, value):
        organization = get_current_organization()
        qs = Category.objects.filter(id=value)
        if organization is not None:
            qs = qs.filter(organization=organization)
        if not qs.exists():
            raise serializers.ValidationError(
                'Category not found or does not belong to your organisation.'
            )
        return value

    def _validate_media_id(self, value, *, expected_type: str, field_name: str):
        if value is None:
            return value
        organization = get_current_organization()
        qs = MediaAsset.objects.filter(id=value, media_type=expected_type)
        if organization is not None:
            qs = qs.filter(organization=organization)
        if not qs.exists():
            raise serializers.ValidationError(
                f'{field_name} not found, wrong type, or outside your organisation.'
            )
        return value

    def validate_audio_media_id(self, value):
        return self._validate_media_id(value, expected_type=MediaAsset.TYPE_AUDIO, field_name='Audio media')

    def validate_video_media_id(self, value):
        return self._validate_media_id(value, expected_type=MediaAsset.TYPE_VIDEO, field_name='Video media')

    def _validate_markdown_field(self, value):
        if not value:
            return value
        try:
            reject_dangerous_markdown(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return value

    def validate_content(self, value):
        return self._validate_markdown_field(value)

    def validate_content_ar(self, value):
        return self._validate_markdown_field(value)

    def validate_attachment_url(self, value):
        return validate_http_url(value, field_name='Attachment URL')

    def _normalize_publish_status(self, validated_data):
        request = self.context.get('request')
        if validated_data.get('status') == 'published' and not _can_publish_directly(request):
            validated_data['status'] = 'pending_review'
            validated_data.pop('published_at', None)
        elif validated_data.get('status') == 'published':
            validated_data['published_at'] = timezone.now()
        return validated_data

    def validate(self, attrs):
        controlled = attrs.get(
            'is_controlled_document',
            getattr(self.instance, 'is_controlled_document', False) if self.instance else False,
        )
        if controlled:
            version = attrs.get(
                'attachment_version',
                getattr(self.instance, 'attachment_version', '') if self.instance else '',
            )
            label = attrs.get(
                'document_label',
                getattr(self.instance, 'document_label', '') if self.instance else '',
            )
            attachment = attrs.get(
                'attachment_url',
                getattr(self.instance, 'attachment_url', '') if self.instance else '',
            )
            errors = {}
            if not (version or '').strip():
                errors['attachment_version'] = 'Version is required for controlled documents.'
            if not (label or '').strip():
                errors['document_label'] = 'Document label is required for controlled documents.'
            if not (attachment or '').strip():
                errors['attachment_url'] = 'Attachment is required for controlled documents.'
            if errors:
                raise serializers.ValidationError(errors)
        return attrs

    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        validated_data['category_id'] = category_id
        if 'audio_media_id' in validated_data:
            validated_data['audio_media_id'] = validated_data.pop('audio_media_id')
        if 'video_media_id' in validated_data:
            validated_data['video_media_id'] = validated_data.pop('video_media_id')
        validated_data['author'] = self.context['request'].user
        validated_data = self._normalize_publish_status(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'category_id' in validated_data:
            validated_data['category_id'] = validated_data.pop('category_id')
        if 'audio_media_id' in validated_data:
            validated_data['audio_media_id'] = validated_data.pop('audio_media_id')
        if 'video_media_id' in validated_data:
            validated_data['video_media_id'] = validated_data.pop('video_media_id')
        validated_data = self._normalize_publish_status(validated_data)
        return super().update(instance, validated_data)
