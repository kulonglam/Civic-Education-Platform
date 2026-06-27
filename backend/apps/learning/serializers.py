from django.utils import timezone
from rest_framework import serializers

from apps.core.sanitize import reject_dangerous_markdown
from apps.core.utils import get_preferred_language
from apps.tenants.context import get_current_organization

from .models import Article, Category


def validate_http_url(value: str, *, field_name: str = 'URL') -> str:
    if not value:
        return value
    value = value.strip()
    if not value.startswith(('http://', 'https://')):
        raise serializers.ValidationError(f'{field_name} must use http or https.')
    return value


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'name_ar', 'description_ar']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and get_preferred_language(request) == 'ar':
            if data.get('name_ar'):
                data['name'] = data['name_ar']
            if data.get('description_ar'):
                data['description'] = data['description_ar']
        return data


class ArticleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True)
    author_name = serializers.CharField(source='author.full_name', read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'title_ar', 'content', 'content_ar',
            'category', 'category_id', 'author', 'author_name',
            'tags', 'featured_image_url', 'attachment_url', 'attachment_name',
            'status', 'published_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'author', 'published_at', 'created_at', 'updated_at']

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
        """Ensure the referenced category belongs to the current tenant."""
        organization = get_current_organization()
        qs = Category.objects.filter(id=value)
        if organization is not None:
            qs = qs.filter(organization=organization)
        if not qs.exists():
            raise serializers.ValidationError(
                'Category not found or does not belong to your organisation.'
            )
        return value

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

    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        validated_data['category_id'] = category_id
        validated_data['author'] = self.context['request'].user
        if validated_data.get('status') == 'published':
            validated_data['published_at'] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'category_id' in validated_data:
            validated_data['category_id'] = validated_data.pop('category_id')
        new_status = validated_data.get('status')
        if new_status == 'published' and instance.status != 'published':
            validated_data['published_at'] = timezone.now()
        return super().update(instance, validated_data)
