import logging

from celery import shared_task

from .models import Article
from .translation import apply_article_translation, apply_record_translation

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def translate_article_task(self, article_id: str):
    """Fill the missing English or Arabic side of an article."""
    try:
        article = Article.all_objects.get(pk=article_id)
    except Article.DoesNotExist:
        logger.warning('Article %s no longer exists; skipping translation', article_id)
        return None
    return apply_article_translation(article)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def translate_record_task(self, app_label: str, model_name: str, pk: str):
    """Fill missing English/Arabic fields on quizzes, news, events, and similar."""
    from django.apps import apps

    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        logger.warning('Unknown translation model %s.%s', app_label, model_name)
        return None
    manager = getattr(model, 'all_objects', model.objects)
    try:
        instance = manager.get(pk=pk)
    except model.DoesNotExist:
        logger.warning('%s %s no longer exists; skipping translation', model_name, pk)
        return None
    return apply_record_translation(instance)
