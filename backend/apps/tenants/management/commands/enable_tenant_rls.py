"""Opt-in Postgres RLS for tenant tables (non-superuser app role)."""

from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from apps.tenants.rls import GUC_ORG, tenant_table_names


POLICY_SQL = """
ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {table} FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON {table};
CREATE POLICY tenant_isolation ON {table}
  USING (
    current_setting('{guc}', true) = ''
    OR organization_id::text = current_setting('{guc}', true)
  )
  WITH CHECK (
    current_setting('{guc}', true) = ''
    OR organization_id::text = current_setting('{guc}', true)
  );
"""


class Command(BaseCommand):
    help = (
        'Enable FORCE ROW LEVEL SECURITY on tenant tables. Use a non-superuser '
        'DATABASE_URL role; table owners that are superusers still bypass RLS.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        if connection.vendor != 'postgresql':
            raise CommandError('enable_tenant_rls requires PostgreSQL.')
        statements = [
            POLICY_SQL.format(table=table, guc=GUC_ORG)
            for table in tenant_table_names()
        ]
        if options['dry_run']:
            self.stdout.write('\n'.join(statements))
            return
        with connection.cursor() as cursor:
            for sql in statements:
                cursor.execute(sql)
        self.stdout.write(self.style.SUCCESS(
            f'RLS enabled on {len(statements)} table(s). '
            'Requests set app.current_organization_id via TenantMiddleware.'
        ))
