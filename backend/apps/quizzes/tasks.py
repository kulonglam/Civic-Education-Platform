import logging

from celery import shared_task

from .models import Certificate

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def generate_certificate_pdf_task(self, certificate_id: str):
    """Render the certificate PDF and upload it to storage off the request path."""
    from .services import generate_certificate_pdf

    try:
        certificate = Certificate.objects.select_related('quiz', 'user').get(id=certificate_id)
    except Certificate.DoesNotExist:
        logger.warning('Certificate %s no longer exists; skipping PDF generation', certificate_id)
        return None

    pdf_url = generate_certificate_pdf(certificate)
    if pdf_url:
        certificate.pdf_url = pdf_url
        certificate.save(update_fields=['pdf_url'])
        logger.info('Certificate %s PDF generated', certificate_id)
    return pdf_url
