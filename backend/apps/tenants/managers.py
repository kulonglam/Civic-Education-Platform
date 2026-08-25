from django.db import models

from .context import get_current_organization, tenant_queries_fail_closed


class TenantQuerySet(models.QuerySet):
    pass


class TenantManager(models.Manager):
    """Manager that automatically scopes queries to the current organization.

    When a request is running inside an organization context, queries are
    filtered to that organization. API requests with no resolved tenant fail
    closed (empty queryset). Django admin, management commands, and tests
    outside middleware still see unscoped results so seed/admin keep working.
    """

    def get_queryset(self):
        qs = TenantQuerySet(self.model, using=self._db)
        organization = get_current_organization()
        if organization is not None:
            return qs.filter(organization=organization)
        if tenant_queries_fail_closed():
            return qs.none()
        return qs
