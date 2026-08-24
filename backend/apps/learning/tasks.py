import logging

from celery import shared_task

from .models import Article
from .translation import apply_article_translation

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
