from django.db import models

from .context import get_current_organization


class TenantQuerySet(models.QuerySet):
    pass


class TenantManager(models.Manager):
    """Manager that automatically scopes queries to the current organization.

    When a request (or task) is running inside an organization context, all
    queries are filtered to that organization. Outside any tenant context
    (Django admin, management commands, superuser tooling, cross-tenant
    analytics) the manager returns unscoped results.
    """

    def get_queryset(self):
        qs = TenantQuerySet(self.model, using=self._db)
        organization = get_current_organization()
        if organization is not None:
            return qs.filter(organization=organization)
        return qs
