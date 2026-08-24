from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engagement', '0006_campaignsignup'),
    ]

    operations = [
        migrations.AddField(
            model_name='civicevent',
            name='region',
            field=models.CharField(
                blank=True,
                db_index=True,
                default='',
                help_text='South Sudan state for the civic map. Blank means nationwide.',
                max_length=40,
            ),
        ),
        migrations.AddField(
            model_name='civicevent',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='civicevent',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
    ]
