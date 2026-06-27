from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0004_article_attachment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='attachment_url',
            field=models.CharField(blank=True, default='', max_length=2048),
        ),
    ]
