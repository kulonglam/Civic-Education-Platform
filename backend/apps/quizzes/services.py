import secrets
from io import BytesIO

from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from apps.core.branding import PLATFORM_NAME
from apps.core.storage import upload_bytesio

from .models import Certificate


def generate_certificate_number():
    date_part = timezone.now().strftime('%Y%m%d')
    random_part = secrets.token_hex(4).upper()
    return f'CEP-{date_part}-{random_part}'


def generate_certificate_pdf(certificate: Certificate) -> str | None:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont('Helvetica-Bold', 24)
    c.drawCentredString(width / 2, height - 100, 'Certificate of Completion')
    c.setFont('Helvetica', 14)
    c.drawCentredString(width / 2, height - 150, PLATFORM_NAME)
    c.setFont('Helvetica', 12)
    c.drawCentredString(width / 2, height - 200, 'This certifies that')
    c.setFont('Helvetica-Bold', 16)
    c.drawCentredString(width / 2, height - 230, certificate.user.full_name)
    c.setFont('Helvetica', 12)
    c.drawCentredString(width / 2, height - 270, 'has successfully completed the quiz:')
    c.drawCentredString(width / 2, height - 300, certificate.quiz.title)
    c.drawCentredString(width / 2, height - 340, f'Certificate No: {certificate.certificate_number}')
    c.drawCentredString(width / 2, height - 360, f'Issued: {certificate.issue_date}')
    c.showPage()
    c.save()

    buffer.seek(0)
    path = f'certificates/{certificate.id}.pdf'
    return upload_bytesio(path, buffer, 'application/pdf')
