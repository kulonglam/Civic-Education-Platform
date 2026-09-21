from django.db import migrations
from django.db.models import F, Value
from django.db.models.functions import Replace

OLD = 'Civic Education RSS'
OLD_SHORT = 'Civic RSS'
OLD_AR = 'التعليم المدني RSS'
NEW = 'CivicHub'


def _replace(model, field, old, new):
    model.objects.filter(**{f'{field}__contains': old}).update(
        **{field: Replace(F(field), Value(old), Value(new))},
    )


def rename_legacy_brand(apps, schema_editor):
    Organization = apps.get_model('tenants', 'Organization')
    Organization.objects.filter(name=OLD).update(name=NEW)
    Organization.objects.filter(name=OLD_SHORT).update(name=NEW)
    Organization.objects.filter(name=OLD_AR).update(name=NEW)

    CivicNews = apps.get_model('engagement', 'CivicNews')
    CivicEvent = apps.get_model('engagement', 'CivicEvent')
    for model, fields in (
        (CivicNews, ('source_name', 'body', 'body_ar', 'title', 'title_ar')),
        (CivicEvent, ('source_name', 'description', 'description_ar', 'title', 'title_ar')),
    ):
        for field in fields:
            _replace(model, field, OLD, NEW)
            _replace(model, field, OLD_SHORT, NEW)
            _replace(model, field, OLD_AR, NEW)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('tenants', '0006_grade_a_enterprise'),
        ('engagement', '0007_civicevent_region_coords'),
    ]

    operations = [
        migrations.RunPython(rename_legacy_brand, noop),
    ]
