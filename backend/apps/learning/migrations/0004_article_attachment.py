from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0003_article_organization_category_organization_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='attachment_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='article',
            name='attachment_url',
            field=models.URLField(blank=True),
        ),
    ]
