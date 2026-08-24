from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_role_super_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='show_on_leaderboard',
            field=models.BooleanField(
                default=True,
                help_text='If false, the learner is omitted from public XP rankings.',
            ),
        ),
    ]
