from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=4000, trim_whitespace=True)
    article_id = serializers.UUIDField(required=False, allow_null=True)


class ChatResponseSerializer(serializers.Serializer):
    session_id = serializers.CharField()
    reply = serializers.CharField()
    tokens_used = serializers.IntegerField()
    messages_used_today = serializers.IntegerField()
    daily_limit = serializers.IntegerField(allow_null=True)


class TutorUsageSerializer(serializers.Serializer):
    daily_limit = serializers.IntegerField(allow_null=True)
    messages_used_today = serializers.IntegerField()
    messages_remaining = serializers.IntegerField(allow_null=True)
    session_message_count = serializers.IntegerField()
