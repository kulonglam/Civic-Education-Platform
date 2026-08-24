import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0011_article_translation'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                (
                    'organization',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='%(class)ss',
                        to='tenants.organization',
                    ),
                ),
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'article',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='bookmarks',
                        to='learning.article',
                    ),
                ),
                (
                    'media',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='bookmarks',
                        to='learning.mediaasset',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='bookmarks',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'db_table': 'bookmarks',
                'ordering': ['-created_at'],
                'constraints': [
                    models.CheckConstraint(
                        condition=(
                            models.Q(('article__isnull', False), ('media__isnull', True))
                            | models.Q(('article__isnull', True), ('media__isnull', False))
                        ),
                        name='bookmark_one_target',
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(('article__isnull', False)),
                        fields=('organization', 'user', 'article'),
                        name='uniq_bookmark_article',
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(('media__isnull', False)),
                        fields=('organization', 'user', 'media'),
                        name='uniq_bookmark_media',
                    ),
                ],
            },
        ),
    ]
