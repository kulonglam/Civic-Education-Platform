from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.notifications.services import notify_all_users
from apps.tutor.document_text import invalidate_attachment_text_cache

from .models import Article
from .tutor_index import build_tutor_index_text


@receiver(pre_save, sender=Article)
def track_attachment_change(sender, instance, **kwargs):
    if not instance.pk:
        instance._prev_attachment_url = ''
        return
    prev = Article.objects.filter(pk=instance.pk).values_list('attachment_url', flat=True).first()
    instance._prev_attachment_url = prev or ''


@receiver(post_save, sender=Article)
def maintain_tutor_index(sender, instance, **kwargs):
    prev_url = getattr(instance, '_prev_attachment_url', '')
    if prev_url and prev_url != (instance.attachment_url or ''):
        invalidate_attachment_text_cache(prev_url)
    if (instance.attachment_url or '') != prev_url and instance.attachment_url:
        invalidate_attachment_text_cache(instance.attachment_url)

    index_text = build_tutor_index_text(instance)
    if index_text != (instance.tutor_index_text or ''):
        Article.objects.filter(pk=instance.pk).update(tutor_index_text=index_text)


@receiver(post_save, sender=Article)
def notify_on_publish(sender, instance, created, **kwargs):
    if instance.status != 'published':
        return
    update_fields = kwargs.get('update_fields')
    if not created and update_fields is not None and 'status' not in update_fields:
        return
    notify_all_users(
        notification_type='new_content',
        title='New civic education article',
        message=f'A new article has been published: {instance.title}',
        organization_id=str(instance.organization_id) if instance.organization_id else None,
    )
