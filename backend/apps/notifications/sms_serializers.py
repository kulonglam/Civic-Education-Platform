from rest_framework import serializers

from .models import SmsMessage


class SendSmsSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=480)
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


class BroadcastSmsSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=480)


class SmsMessageSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True, default=None)

    class Meta:
        model = SmsMessage
        fields = [
            'id',
            'user',
            'user_email',
            'phone',
            'message',
            'message_type',
            'status',
            'provider_reference',
            'error_detail',
            'sent_at',
            'created_at',
        ]
        read_only_fields = fields
