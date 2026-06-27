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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organizations'
        ordering = ['name']

    def __str__(self):
        return self.name


class Membership(models.Model):
    OWNER = 'owner'
    ADMIN = 'admin'
    MEMBER = 'member'
    ROLE_CHOICES = [
        (OWNER, 'Owner'),
        (ADMIN, 'Admin'),
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
