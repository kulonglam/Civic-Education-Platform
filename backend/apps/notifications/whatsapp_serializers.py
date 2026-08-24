from rest_framework import serializers

from .models import WhatsAppMessage


class SendWhatsAppSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
    )
    phones = serializers.ListField(
        child=serializers.CharField(max_length=20),
        required=False,
        allow_empty=True,
    )

    def validate(self, attrs):
        if not attrs.get('user_ids') and not attrs.get('phones'):
            raise serializers.ValidationError(
                'Provide at least one user_id or phone number.',
            )
        return attrs


class BroadcastWhatsAppSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)


class WhatsAppMessageSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True, default=None)

    class Meta:
        model = WhatsAppMessage
        fields = [
            'id',
            'user',
            'user_email',
            'phone',
            'message',
            'message_type',
            'direction',
            'status',
            'provider_reference',
            'error_detail',
            'sent_at',
            'created_at',
        ]
        read_only_fields = fields
