from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    """Generic ``{"message": "..."}`` response body."""

    message = serializers.CharField()


class DetailSerializer(serializers.Serializer):
    """Generic ``{"detail": "..."}`` response body."""

    detail = serializers.CharField()


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()


class PublicConfigSerializer(serializers.Serializer):
    platform_name = serializers.CharField()
    support_email = serializers.CharField(allow_blank=True)
