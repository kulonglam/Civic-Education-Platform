from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_product_features'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='mfa_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='totp_secret',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
    ]
