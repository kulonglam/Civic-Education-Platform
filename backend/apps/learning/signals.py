from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notifications.services import notify_all_users

from .models import Article


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
