import secrets
from io import BytesIO

from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from apps.core.branding import PLATFORM_NAME
from apps.core.storage import upload_bytesio

from .models import Certificate, Question, Quiz


def generate_certificate_number():
    date_part = timezone.now().strftime('%Y%m%d')
    random_part = secrets.token_hex(4).upper()
    return f'CEP-{date_part}-{random_part}'


def option_feedback_text(question: Question, user_answer: str, *, lang: str = 'en') -> str:
    """Teaching note for the choice the learner made, falling back to the question explanation."""
    options = question.options or []
    entries = question.option_feedback or []
    try:
        index = options.index(user_answer)
    except ValueError:
        index = -1
    if 0 <= index < len(entries):
        entry = entries[index]
        if isinstance(entry, dict):
            if lang == 'ar' and entry.get('ar'):
                return entry['ar']
            if entry.get('en'):
                return entry['en']
        elif isinstance(entry, str) and entry:
            return entry
    if lang == 'ar' and question.explanation_ar:
        return question.explanation_ar
    return question.explanation or ''


def grade_answer(question: Question, user_answer: str) -> bool:
    return (user_answer or '') == question.correct_answer


def build_review_item(question: Question, user_answer: str, *, lang: str = 'en') -> dict:
    is_correct = grade_answer(question, user_answer)
    awarded = question.points if is_correct else 0
    use_ar = lang == 'ar'
    question_text = (
        question.question_text_ar if use_ar and question.question_text_ar else question.question_text
    )
    explanation = option_feedback_text(question, user_answer, lang=lang)
    return {
        'question_id': str(question.id),
        'question_type': question.question_type,
        'question_text': question_text,
        'learner_answer': user_answer or '',
        'correct_answer': question.correct_answer,
        'is_correct': is_correct,
        'points': question.points,
        'points_awarded': awarded,
        'explanation': explanation,
    }


def score_quiz(quiz: Quiz, answers: dict, *, lang: str = 'en') -> dict:
    review = []
    raw_score = 0
    max_raw = 0
    for question in quiz.questions.all():
        max_raw += question.points
        user_answer = answers.get(str(question.id), '')
        item = build_review_item(question, user_answer, lang=lang)
        raw_score += item['points_awarded']
        review.append(item)
    percentage = int((raw_score / max_raw * 100)) if max_raw > 0 else 0
    return {
        'percentage': percentage,
        'passed': percentage >= quiz.passing_score,
        'review': review,
    }


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
