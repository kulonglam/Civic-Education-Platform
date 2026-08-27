from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0013_course_courselesson'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='featured_image_url',
            field=models.CharField(blank=True, default='', max_length=2048),
        ),
    ]
