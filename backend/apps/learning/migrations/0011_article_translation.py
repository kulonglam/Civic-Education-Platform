from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0010_article_tutor_index_text_mediaasset_captions_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='source_language',
            field=models.CharField(
                blank=True,
                choices=[('en', 'English'), ('ar', 'Arabic')],
                default='',
                help_text='Detected language of the author-written side.',
                max_length=2,
            ),
        ),
        migrations.AddField(
            model_name='article',
            name='translation_status',
            field=models.CharField(
                choices=[
                    ('none', 'None'),
                    ('machine', 'Machine'),
                    ('failed', 'Failed'),
                ],
                db_index=True,
                default='none',
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name='article',
            name='translated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='translation_fingerprint',
            field=models.CharField(
                blank=True,
                default='',
                help_text='SHA-256 of the source title+body that produced the current translation.',
                max_length=64,
            ),
        ),
    ]
