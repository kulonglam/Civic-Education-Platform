"""Postgres session GUCs for optional row-level security.

Django's default database role is typically the table owner, which bypasses
RLS unless FORCE ROW LEVEL SECURITY is applied to a non-superuser role.
``enable_tenant_rls`` is opt-in for that production layout. The session GUC
is still set on every request so policies work as soon as they are enabled.
"""

from __future__ import annotations

from django.db import connection


GUC_ORG = 'app.current_organization_id'


def apply_rls_session(organization=None) -> None:
    """Bind (or clear) the current org id on the Postgres session."""
    if connection.vendor != 'postgresql':
        return
    org_id = str(organization.id) if organization is not None else ''
    with connection.cursor() as cursor:
        cursor.execute("SELECT set_config(%s, %s, false)", [GUC_ORG, org_id])


def tenant_table_names():
    from django.apps import apps

    from .models import TenantModel

    tables = []
    for model in apps.get_models():
        if not issubclass(model, TenantModel) or model._meta.abstract:
            continue
        tables.append(model._meta.db_table)
    tables.append('activity_logs')
    return sorted(set(tables))
