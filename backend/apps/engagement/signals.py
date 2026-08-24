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


@receiver(post_save, sender='engagement.Poll')
def enqueue_poll_translation(sender, instance, **kwargs):
    _enqueue(instance)


@receiver(post_save, sender='engagement.PollOption')
def enqueue_poll_option_translation(sender, instance, **kwargs):
    _enqueue(instance)


@receiver(post_save, sender='engagement.Petition')
def enqueue_petition_translation(sender, instance, **kwargs):
    _enqueue(instance)


@receiver(post_save, sender='engagement.Campaign')
def enqueue_campaign_translation(sender, instance, **kwargs):
    _enqueue(instance)


@receiver(post_save, sender='engagement.CivicNews')
def enqueue_news_translation(sender, instance, **kwargs):
    _enqueue(instance)


@receiver(post_save, sender='engagement.CivicEvent')
def enqueue_event_translation(sender, instance, **kwargs):
    _enqueue(instance)
