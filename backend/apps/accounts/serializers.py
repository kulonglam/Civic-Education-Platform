from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from apps.core.constants import LANGUAGE_CHOICES

from .mfa import user_has_mfa_enabled, user_requires_mfa
from .models import Role, UserProfile

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar_url', 'preferred_language']


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    profile = UserProfileSerializer(read_only=True)
    mfa_required = serializers.SerializerMethodField()
    mfa_enabled = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone', 'first_name', 'last_name', 'role',
            'is_active', 'is_suspended', 'email_verified', 'phone_verified',
            'created_at', 'profile', 'mfa_required', 'mfa_enabled',
        ]
        read_only_fields = fields

    def get_mfa_required(self, obj):
        return user_requires_mfa(obj)

    def get_mfa_enabled(self, obj):
        return user_has_mfa_enabled(obj)


class RegisterSerializer(serializers.ModelSerializer):
    ACCOUNT_CITIZEN = 'citizen'
    ACCOUNT_ORGANIZATION = 'organization'

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    account_type = serializers.ChoiceField(
        choices=[ACCOUNT_CITIZEN, ACCOUNT_ORGANIZATION],
        write_only=True,
        required=False,
        default=ACCOUNT_CITIZEN,
    )
    organization_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    invite_token = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'account_type',
            'organization_name', 'invite_token',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        validate_password(attrs['password'])

        invite_token = (attrs.get('invite_token') or '').strip()
        if invite_token:
            from apps.tenants.services import get_valid_invite

            invite = get_valid_invite(invite_token)
            if invite is None:
                raise serializers.ValidationError({'invite_token': 'Invalid or expired invitation.'})
            if attrs['email'].lower() != invite.email.lower():
                raise serializers.ValidationError({
                    'email': 'Register with the email address that received the invitation.',
                })
        return attrs

    def create(self, validated_data):
        from apps.billing.services import check_quota
        from apps.tenants.services import (
            accept_organization_invite,
            create_organization_with_owner,
            get_valid_invite,
            join_public_organization,
        )

        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        account_type = validated_data.pop('account_type', self.ACCOUNT_CITIZEN)
        org_name = (validated_data.pop('organization_name', '') or '').strip()
        invite_token = (validated_data.pop('invite_token', '') or '').strip()

        if invite_token:
            invite = get_valid_invite(invite_token)
            citizen_role, _ = Role.objects.get_or_create(name=Role.CITIZEN)
            user = User.objects.create_user(password=password, role=citizen_role, **validated_data)
            check_quota(invite.organization, 'members')
            accept_organization_invite(invite=invite, user=user)
            return user

        if account_type == self.ACCOUNT_ORGANIZATION:
            # Org owners get editor (content tools), not platform admin.
            editor_role, _ = Role.objects.get_or_create(name=Role.EDITOR)
            user = User.objects.create_user(password=password, role=editor_role, **validated_data)
            if not org_name:
                org_name = f"{user.first_name}'s Organization".strip()
            create_organization_with_owner(name=org_name, owner=user)
            return user

        citizen_role, _ = Role.objects.get_or_create(name=Role.CITIZEN)
        user = User.objects.create_user(password=password, role=citizen_role, **validated_data)
        join_public_organization(user)
        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    avatar_url = serializers.URLField(required=False, allow_blank=True)
    preferred_language = serializers.ChoiceField(
        choices=LANGUAGE_CHOICES, required=False
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'bio', 'avatar_url', 'preferred_language']

    def validate_phone(self, value):
        if value in (None, ''):
            return None
        from apps.notifications.sms_services import normalize_phone

        return normalize_phone(value)

    def update(self, instance, validated_data):
        profile_fields = {}
        for field in ('bio', 'avatar_url', 'preferred_language'):
            if field in validated_data:
                profile_fields[field] = validated_data.pop(field)
        if 'phone' in validated_data and validated_data['phone'] != instance.phone:
            instance.phone_verified = False
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if profile_fields:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_fields.items():
                setattr(profile, attr, value)
            profile.save()
        return instance


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        validate_password(attrs['password'])
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({'uid': 'Invalid user.'}) from None
        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError({'token': 'Invalid or expired token.'})
        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['password'])
        user.save()
        return user


class PasswordResetOtpRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)


class PasswordResetOtpConfirmSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        validate_password(attrs['password'])
        from apps.accounts.models import PhoneOTP
        from apps.notifications.sms_services import verify_phone_otp

        try:
            otp = verify_phone_otp(
                phone=attrs['phone'],
                code=attrs['code'],
                purpose=PhoneOTP.PURPOSE_RESET,
            )
        except ValueError as exc:
            raise serializers.ValidationError({'code': str(exc)}) from exc
        attrs['user'] = otp.user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['password'])
        user.save()
        return user


class PhoneVerifyConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        from apps.accounts.models import PhoneOTP
        from apps.notifications.sms_services import verify_phone_otp

        user = self.context['request'].user
        if not user.phone:
            raise serializers.ValidationError({'phone': 'Add a phone number to your profile first.'})
        try:
            verify_phone_otp(
                phone=user.phone,
                code=attrs['code'],
                purpose=PhoneOTP.PURPOSE_VERIFY,
            )
        except ValueError as exc:
            raise serializers.ValidationError({'code': str(exc)}) from exc
        return attrs


class UserRoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=[name for name, _ in Role.ROLE_CHOICES])
