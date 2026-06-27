from django.db import migrations

LEGACY_BLUE = (
    '#2563eb',
    '#3b82f6',
    '#1d4ed8',
    '#1e40af',
    '#1e3a8a',
    '#60a5fa',
    '#93c5fd',
    '#bfdbfe',
    '#dbeafe',
    '#eff6ff',
)
GREEN = '#059669'


def migrate_blue_to_green(apps, schema_editor):
    Organization = apps.get_model('tenants', 'Organization')
    for legacy in LEGACY_BLUE:
        Organization.objects.filter(primary_color__iexact=legacy).update(primary_color=GREEN)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('tenants', '0002_organization_invites'),
    ]

    operations = [
        migrations.RunPython(migrate_blue_to_green, noop),
    ]
