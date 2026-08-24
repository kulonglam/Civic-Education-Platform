"""Add Super Admin platform role for system configuration and security."""

from django.db import migrations, models


def create_super_admin_role(apps, schema_editor):
    Role = apps.get_model('accounts', 'Role')
    Role.objects.get_or_create(name='super_admin')


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_userprofile_region_age_band'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(
                choices=[
                    ('citizen', 'Citizen / Learner'),
                    ('moderator', 'Moderator'),
                    ('editor', 'Content Creator'),
                    ('admin', 'Administrator'),
                    ('super_admin', 'Super Admin'),
                ],
                max_length=20,
                unique=True,
            ),
        ),
        migrations.RunPython(create_super_admin_role, noop),
    ]
