from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0005_quiz_kind_feedback_question_explanation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.CharField(
                choices=[
                    ('mcq', 'Multiple Choice'),
                    ('true_false', 'True/False'),
                    ('scenario', 'Scenario'),
                ],
                default='mcq',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='question',
            name='option_feedback',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='Per-option teaching notes: list of {en, ar} aligned with options.',
            ),
        ),
    ]
