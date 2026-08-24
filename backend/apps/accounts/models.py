import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from apps.accounts.demographics import AGE_BAND_CHOICES, REGION_CHOICES
from apps.core.constants import DEFAULT_LANGUAGE, LANGUAGE_CHOICES


class Role(models.Model):
    CITIZEN = 'citizen'
    MODERATOR = 'moderator'
    EDITOR = 'editor'
    ADMIN = 'admin'
    SUPER_ADMIN = 'super_admin'

    ROLE_CHOICES = [
        (CITIZEN, 'Citizen / Learner'),
        (MODERATOR, 'Moderator'),
        (EDITOR, 'Content Creator'),
        (ADMIN, 'Administrator'),
        (SUPER_ADMIN, 'Super Admin'),
    ]

    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        role = extra_fields.pop('role', None)
        if role is None:
            role, _ = Role.objects.get_or_create(name=Role.CITIZEN)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        role, _ = Role.objects.get_or_create(name=Role.SUPER_ADMIN)
        extra_fields['role'] = role
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='users')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()


class UserProfile(models.Model):
    LANGUAGE_CHOICES = LANGUAGE_CHOICES

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)
    preferred_language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default=DEFAULT_LANGUAGE,
    )
    totp_secret = models.CharField(max_length=64, blank=True, default='')
    mfa_enabled = models.BooleanField(default=False)
    session_epoch = models.PositiveIntegerField(
        default=0,
        help_text='Incremented to revoke all outstanding JWTs for this user.',
    )
    xp_points = models.PositiveIntegerField(default=0)
    region = models.CharField(
        max_length=40,
        choices=REGION_CHOICES,
        blank=True,
        default='',
        help_text='Optional state or area used only in aggregated poll summaries.',
    )
    age_band = models.CharField(
        max_length=20,
        choices=AGE_BAND_CHOICES,
        blank=True,
        default='',
        help_text='Optional age range used only in aggregated poll summaries.',
    )

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f'Profile: {self.user.email}'


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        db_table = 'email_verification_tokens'


class PhoneOTP(models.Model):
    PURPOSE_RESET = 'password_reset'
    PURPOSE_VERIFY = 'phone_verify'
    PURPOSE_CHOICES = [
        (PURPOSE_RESET, 'Password Reset'),
        (PURPOSE_VERIFY, 'Phone Verification'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phone_otps')
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        db_table = 'phone_otps'
        indexes = [models.Index(fields=['phone', 'purpose', 'used'])]
