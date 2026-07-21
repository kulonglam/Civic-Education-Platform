from rest_framework import serializers

from apps.core.constants import DEFAULT_PRIMARY_COLOR, normalize_primary_color

from .models import (
    Department,
    Membership,
    Organization,
    OrganizationInvite,
    OrganizationSsoConfig,
    SupportCase,
)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'tagline', 'logo_url', 'primary_color',
            'is_active', 'force_mfa_for_admins', 'audit_retention_days',
            'ip_allowlist', 'created_at',
        ]
        read_only_fields = ['id', 'slug', 'is_active', 'created_at']

    def validate_ip_allowlist(self, value):
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError('ip_allowlist must be a list of IP/CIDR strings.')
        cleaned = []
        for entry in value:
            text = str(entry).strip()
            if text:
                cleaned.append(text)
        return cleaned

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['primary_color'] = normalize_primary_color(data.get('primary_color'))
        return data


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'slug', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrganizationSsoConfigSerializer(serializers.ModelSerializer):
    client_secret = serializers.CharField(write_only=True, required=False, allow_blank=True)
    has_client_secret = serializers.SerializerMethodField()
    is_ready = serializers.BooleanField(read_only=True)

    class Meta:
        model = OrganizationSsoConfig
        fields = [
            'id', 'enabled', 'issuer', 'client_id', 'client_secret', 'scopes',
            'has_client_secret', 'is_ready', 'updated_at',
        ]
        read_only_fields = ['id', 'has_client_secret', 'is_ready', 'updated_at']

    def get_has_client_secret(self, obj):
        return bool(obj.client_secret)

    def update(self, instance, validated_data):
        secret = validated_data.pop('client_secret', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if secret:
            instance.client_secret = secret
        instance.save()
        return instance


class MemberInviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=Membership.ROLE_CHOICES,
        default=Membership.MEMBER,
    )
    department_id = serializers.UUIDField(required=False, allow_null=True)


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True, allow_null=True)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Membership
        fields = [
            'id', 'user', 'user_email', 'user_name', 'user_phone', 'role',
            'department', 'department_id', 'created_at',
        ]
        read_only_fields = ['id', 'user', 'user_email', 'user_name', 'user_phone', 'created_at']


class UserOrganizationMembershipSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ['id', 'role', 'organization', 'created_at']
        read_only_fields = fields


class MemberRoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=Membership.ROLE_CHOICES)
    department_id = serializers.UUIDField(required=False, allow_null=True)


class OrganizationInviteSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = OrganizationInvite
        fields = [
            'id', 'email', 'role', 'department', 'organization_name',
            'created_at', 'expires_at', 'accepted_at',
        ]
        read_only_fields = fields


class InvitePreviewSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.CharField()
    organization = OrganizationSerializer()
    expires_at = serializers.DateTimeField()
    is_expired = serializers.BooleanField()


class BulkImportRowSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    role = serializers.ChoiceField(choices=Membership.ROLE_CHOICES, default=Membership.MEMBER)
    department = serializers.CharField(required=False, allow_blank=True, max_length=150)


class BulkImportSerializer(serializers.Serializer):
    rows = BulkImportRowSerializer(many=True)
    dry_run = serializers.BooleanField(default=False)
    send_invites = serializers.BooleanField(default=True)


class PlatformOrganizationSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True)
    plan_code = serializers.CharField(read_only=True, allow_null=True)

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'tagline', 'is_active', 'member_count',
            'plan_code', 'created_at',
        ]
        read_only_fields = fields


class SupportCaseSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)

    class Meta:
        model = SupportCase
        fields = [
            'id', 'organization', 'organization_name', 'created_by', 'created_by_email',
            'subject', 'body', 'status', 'priority', 'assignee_notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'organization', 'organization_name', 'created_by', 'created_by_email',
            'created_at', 'updated_at',
        ]
