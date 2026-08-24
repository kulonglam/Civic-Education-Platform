"""Enqueue automatic translation for articles missing English or Arabic."""

from django.core.management.base import BaseCommand

from apps.learning.models import Article
from apps.learning.tasks import translate_article_task
from apps.learning.translation import resolve_translation_job, source_fingerprint


class Command(BaseCommand):
    help = 'Translate articles that are missing an English or Arabic side.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='List articles that would be translated without enqueueing tasks.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Maximum number of articles to process.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        queued = 0

        qs = Article.all_objects.order_by('created_at')
        for article in qs.iterator():
            job = resolve_translation_job(article)
            if job is None:
                continue
            fingerprint = source_fingerprint(job.source_title, job.source_content)
            if fingerprint and fingerprint == (article.translation_fingerprint or ''):
                continue
            if dry_run:
                self.stdout.write(f'{article.pk}  {job.kind}  {article.title[:60]}')
            else:
                translate_article_task.delay(str(article.pk))
            queued += 1
            if limit is not None and queued >= limit:
                break

        action = 'Would translate' if dry_run else 'Queued'
        self.stdout.write(self.style.SUCCESS(f'{action} {queued} article(s).'))
