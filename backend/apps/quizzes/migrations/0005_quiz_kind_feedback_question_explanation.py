from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0004_question_options_ar'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='kind',
            field=models.CharField(
                choices=[('practice', 'Practice'), ('assessment', 'Final assessment')],
                default='assessment',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='quiz',
            name='feedback_mode',
            field=models.CharField(
                choices=[('end', 'After submit'), ('per_question', 'After each question')],
                default='end',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='quiz',
            name='max_attempts',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Blank means unlimited attempts.',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='question',
            name='explanation',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='question',
            name='explanation_ar',
            field=models.TextField(blank=True),
        ),
    ]
