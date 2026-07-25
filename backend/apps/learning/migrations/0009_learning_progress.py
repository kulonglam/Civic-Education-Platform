import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0008_media_assets'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleProgress',
            fields=[
                ('organization', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(class)ss',
                    to='tenants.organization',
                )),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('progress_percent', models.PositiveSmallIntegerField(default=0)),
                ('completed', models.BooleanField(db_index=True, default=False)),
                ('last_viewed_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('article', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='progress_records',
                    to='learning.article',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='article_progress',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'article_progress',
                'ordering': ['-last_viewed_at'],
                'unique_together': {('organization', 'user', 'article')},
            },
        ),
        migrations.CreateModel(
            name='MediaProgress',
            fields=[
                ('organization', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(class)ss',
                    to='tenants.organization',
                )),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('completed', models.BooleanField(db_index=True, default=False)),
                ('last_viewed_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('media', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='progress_records',
                    to='learning.mediaasset',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='media_progress',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'media_progress',
                'ordering': ['-last_viewed_at'],
                'unique_together': {('organization', 'user', 'media')},
            },
        ),
    ]
