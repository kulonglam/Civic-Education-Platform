from rest_framework import serializers


class BroadcastNotificationSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    message = serializers.CharField(max_length=2000)
    notification_type = serializers.ChoiceField(
        choices=['announcement', 'new_content'],
        default='announcement',
    )


class WebPushSubscribeSerializer(serializers.Serializer):
    endpoint = serializers.URLField()
    keys = serializers.DictField(child=serializers.CharField())

    def validate_keys(self, value):
        if not value.get('p256dh') or not value.get('auth'):
            raise serializers.ValidationError('keys must include p256dh and auth.')
        return value
