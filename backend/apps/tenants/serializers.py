from rest_framework import serializers

from apps.core.constants import DEFAULT_PRIMARY_COLOR, normalize_primary_color

from .models import Membership, Organization, OrganizationInvite


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'tagline', 'logo_url', 'primary_color',
            'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'slug', 'is_active', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['primary_color'] = normalize_primary_color(data.get('primary_color'))
        return data


class MemberInviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=Membership.ROLE_CHOICES,
        default=Membership.MEMBER,
    )


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True, allow_null=True)

    class Meta:
        model = Membership
        fields = ['id', 'user', 'user_email', 'user_name', 'user_phone', 'role', 'created_at']
        read_only_fields = ['id', 'user', 'user_email', 'user_name', 'user_phone', 'created_at']


class UserOrganizationMembershipSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = ['id', 'role', 'organization', 'created_at']
        read_only_fields = fields


class MemberRoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=Membership.ROLE_CHOICES)


class OrganizationInviteSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = OrganizationInvite
        fields = [
            'id', 'email', 'role', 'organization_name', 'created_at', 'expires_at', 'accepted_at',
        ]
        read_only_fields = fields


class InvitePreviewSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.CharField()
    organization = OrganizationSerializer()
    expires_at = serializers.DateTimeField()
    is_expired = serializers.BooleanField()
