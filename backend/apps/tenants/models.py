import secrets
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.constants import DEFAULT_PRIMARY_COLOR

from .context import get_current_organization
from .managers import TenantManager


class Organization(models.Model):
    """A tenant. All customer data is isolated per organization."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    tagline = models.CharField(max_length=255, blank=True)
    logo_url = models.URLField(blank=True)
    primary_color = models.CharField(max_length=7, default=DEFAULT_PRIMARY_COLOR)
    is_active = models.BooleanField(default=True)
    force_mfa_for_admins = models.BooleanField(
        default=True,
        help_text='Require MFA for organization owners and admins.',
    )
    audit_retention_days = models.PositiveIntegerField(
        default=365,
        help_text='Days to retain activity logs for this organization (0 = keep forever).',
    )
    ip_allowlist = models.JSONField(
        default=list,
        blank=True,
        help_text='Optional list of CIDR/IP strings. Empty = allow all client IPs.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organizations'
        ordering = ['name']

    def __str__(self):
        return self.name


class Department(models.Model):
    """Organizational unit within a tenant (ministry division, county office, etc.)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='departments',
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'departments'
        ordering = ['name']
        unique_together = [('organization', 'slug'), ('organization', 'name')]

    def __str__(self):
        return f'{self.name} ({self.organization_id})'


class OrganizationSsoConfig(models.Model):
    """Per-organization OpenID Connect settings (Enterprise plan)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='sso_config',
    )
    enabled = models.BooleanField(default=False)
    issuer = models.URLField(blank=True)
    client_id = models.CharField(max_length=255, blank=True)
    client_secret = models.CharField(max_length=512, blank=True)
    scopes = models.CharField(max_length=255, blank=True, default='openid email profile')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'organization_sso_configs'

    def __str__(self):
        return f'SSO config for {self.organization_id}'

    @property
    def is_ready(self) -> bool:
        return bool(self.enabled and self.issuer and self.client_id and self.client_secret)


class Membership(models.Model):
    OWNER = 'owner'
    ADMIN = 'admin'
    CONTENT_MANAGER = 'content_manager'
    MODERATOR = 'moderator'
    MEMBER = 'member'
    ROLE_CHOICES = [
        (OWNER, 'Owner'),
        (ADMIN, 'Admin'),
        (CONTENT_MANAGER, 'Content manager'),
        (MODERATOR, 'Moderator'),
        (MEMBER, 'Member'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=MEMBER)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='memberships',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'memberships'
        unique_together = [('organization', 'user')]

    def __str__(self):
        return f'{self.user_id} @ {self.organization_id} ({self.role})'


class OrganizationInvite(models.Model):
    """Pending email invitation to join an organization."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='invites',
    )
    email = models.EmailField(db_index=True)
    role = models.CharField(max_length=20, choices=Membership.ROLE_CHOICES, default=Membership.MEMBER)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invites',
    )
    token = models.CharField(max_length=64, unique=True, db_index=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_org_invites',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'organization_invites'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'email'],
                condition=models.Q(accepted_at__isnull=True),
                name='unique_pending_invite_per_org_email',
            ),
        ]

    def __str__(self):
        return f'Invite {self.email} → {self.organization_id}'

    @property
    def is_pending(self):
        return self.accepted_at is None and self.expires_at > timezone.now()

    @classmethod
    def generate_token(cls):
        return secrets.token_urlsafe(32)


class OrganizationScimToken(models.Model):
    """Bearer token for SCIM 2.0 provisioning integrations (hashed at rest)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='scim_tokens',
    )
    name = models.CharField(max_length=100, default='SCIM token')
    token_prefix = models.CharField(max_length=12, blank=True)
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'organization_scim_tokens'
        ordering = ['-created_at']

    def __str__(self):
        return f'SCIM token {self.token_prefix}… ({self.organization_id})'


class SupportCase(models.Model):
    """Tenant-raised support case visible to platform operators."""

    STATUS_OPEN = 'open'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_RESOLVED = 'resolved'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_CLOSED, 'Closed'),
    ]
    PRIORITY_LOW = 'low'
    PRIORITY_NORMAL = 'normal'
    PRIORITY_HIGH = 'high'
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_NORMAL, 'Normal'),
        (PRIORITY_HIGH, 'High'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='support_cases',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='support_cases_created',
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL)
    assignee_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'support_cases'
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.subject} ({self.status})'


class TenantModel(models.Model):
    """Abstract base for all tenant-owned resources.

    Adds an ``organization`` FK, a tenant-scoped default manager, and an
    ``all_objects`` escape hatch for cross-tenant access. On save, the
    organization is auto-populated from the current tenant context when not
    set explicitly.
    """

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        null=True,
        blank=True,
        db_index=True,
    )

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.organization_id is None:
            current = get_current_organization()
            if current is not None:
                self.organization = current
            else:
                raise ValueError(
                    f'{self.__class__.__name__}.save() called with no organization '
                    'and no active tenant context. Set organization explicitly or '
                    'activate a tenant context before writing.'
                )
        super().save(*args, **kwargs)
