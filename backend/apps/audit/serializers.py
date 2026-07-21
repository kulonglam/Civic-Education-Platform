from rest_framework import serializers

from apps.audit.models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True, default=None)
    user_name = serializers.CharField(source='user.full_name', read_only=True, default=None)
    organization_name = serializers.CharField(source='organization.name', read_only=True, default=None)

    class Meta:
        model = ActivityLog
        fields = [
            'id', 'organization', 'organization_name', 'user', 'user_email', 'user_name',
            'activity_type', 'metadata', 'ip_address', 'user_agent', 'timestamp',
            'prev_hash', 'integrity_hash',
        ]
        read_only_fields = fields
