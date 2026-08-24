from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


def _enqueue(instance):
    if not getattr(settings, 'TRANSLATION_ENABLED', True):
        return
    from apps.learning.tasks import translate_record_task

    translate_record_task.delay(
        instance._meta.app_label,
        instance._meta.model_name,
        str(instance.pk),
    )


@receiver(post_save, sender='quizzes.Quiz')
def enqueue_quiz_translation(sender, instance, **kwargs):
    _enqueue(instance)


@receiver(post_save, sender='quizzes.Question')
def enqueue_question_translation(sender, instance, **kwargs):
    _enqueue(instance)
