import pytest
from django.core.cache import cache
from io import BytesIO
from reportlab.pdfgen import canvas

from apps.learning.models import Article, Category
from apps.tutor.document_text import extract_pdf_text, get_attachment_text
from apps.tutor.retrieval import (
    CATEGORY_SLUGS,
    chunk_text,
    detect_query_categories,
    format_retrieved_context,
    retrieve_article_chunks,
)
from apps.tenants.context import set_current_organization


def _make_pdf(text: str) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(72, 720, text)
    c.save()
    return buf.getvalue()


@pytest.mark.django_db
class TestTutorRetrieval:
    def test_chunk_text_splits_long_document(self):
        text = ('Article 14. Equality before the law. ' * 80).strip()
        chunks = chunk_text(text, size=200, overlap=40)
        assert len(chunks) > 1
        assert all(len(c) <= 240 for c in chunks)

    def test_detect_query_categories(self):
        tokens = {'election', 'vote', 'candidate'}
        assert detect_query_categories(tokens) == {'elections'}

    def test_retrieves_constitution_chunks(self, org, admin_user):
        set_current_organization(org)
        category = Category.objects.create(
            organization=org,
            name='Constitution',
            slug='constitution',
        )
        Article.objects.create(
            organization=org,
            title='Understanding the Transitional Constitution',
            content=(
                'PART TWO BILL OF RIGHTS. Article 14. Equality before the Law. '
                'All persons are equal before the law and are entitled to the equal '
                'protection of the law without discrimination as to race, ethnic origin, '
                'colour, sex, language, religious creed, political opinion, birth, '
                'locality or social status. Article 24. Freedom of Expression and Media. '
                'Every citizen shall have the right to the freedom of expression, reception '
                'and dissemination of information, publication, and access to the press '
                'without prejudice to public order, morality and the integrity of others.'
            ),
            category=category,
            author=admin_user,
            status='published',
            is_controlled_document=True,
            document_label='Transitional Constitution of the Republic of South Sudan, 2011',
            attachment_version='2011',
        )
        Article.objects.create(
            organization=org,
            title='How Local Government Works',
            content='States and counties deliver education and community development services.',
            category=Category.objects.create(
                organization=org, name='Governance', slug='governance'
            ),
            author=admin_user,
            status='published',
        )

        chunks = retrieve_article_chunks('What does Article 14 say about equality before the law?')
        assert chunks, 'Expected constitution chunks for equality query'
        assert any('Equality' in c['text'] or 'equality' in c['text'].lower() for c in chunks)
        assert any('Constitution' in c['source'] for c in chunks)

        formatted = format_retrieved_context(chunks)
        assert 'Source:' in formatted
        assert 'Equality' in formatted or 'equality' in formatted.lower()
        assert 'four categories' in formatted

    def test_retrieves_pdf_attachment_when_body_is_short(self, org, admin_user, settings, tmp_path):
        set_current_organization(org)
        settings.MEDIA_ROOT = tmp_path
        media_dir = tmp_path / 'articles' / str(org.id)
        media_dir.mkdir(parents=True)
        pdf_path = media_dir / 'elections-guide.pdf'
        pdf_bytes = _make_pdf(
            'Voters must register before election day. Ballots are counted transparently.'
        )
        pdf_path.write_bytes(pdf_bytes)

        category = Category.objects.create(
            organization=org, name='Elections', slug='elections'
        )
        Article.objects.create(
            organization=org,
            title='Elections overview',
            content='See the attached PDF for full voter guidance.',
            category=category,
            author=admin_user,
            status='published',
            attachment_url=f'/media/articles/{org.id}/elections-guide.pdf',
            attachment_name='elections-guide.pdf',
        )

        cache.clear()
        chunks = retrieve_article_chunks('How do voters register before election day?')
        assert chunks
        assert any('register' in c['text'].lower() for c in chunks)
        assert any('Elections' in c['source'] for c in chunks)
        assert any(c.get('category_slug') == 'elections' for c in chunks)

    def test_category_routing_prefers_peacebuilding(self, org, admin_user):
        set_current_organization(org)
        peace = Category.objects.create(
            organization=org, name='Peacebuilding', slug='peacebuilding'
        )
        Article.objects.create(
            organization=org,
            title='Community dialogue for reconciliation',
            content=(
                'Peacebuilding requires dialogue between communities, trust-building, '
                'and reconciliation after conflict. Mediation helps resolve disputes peacefully.'
            ),
            category=peace,
            author=admin_user,
            status='published',
        )
        Article.objects.create(
            organization=org,
            title='Election turnout basics',
            content='Election turnout measures how many registered voters cast ballots.',
            category=Category.objects.create(
                organization=org, name='Elections', slug='elections'
            ),
            author=admin_user,
            status='published',
        )

        chunks = retrieve_article_chunks('How does community dialogue support peacebuilding?')
        assert chunks
        assert chunks[0]['category_slug'] == 'peacebuilding'

    def test_all_four_categories_defined(self):
        assert len(CATEGORY_SLUGS) == 4


@pytest.mark.django_db
class TestDocumentText:
    def test_extract_pdf_text(self):
        text = extract_pdf_text(_make_pdf('Article 9. Citizenship and nationality.'))
        assert 'Article 9' in text
        assert 'Citizenship' in text

    def test_get_attachment_text_caches_local_pdf(self, settings, tmp_path):
        settings.MEDIA_ROOT = tmp_path
        pdf_path = tmp_path / 'articles' / 'org' / 'doc.pdf'
        pdf_path.parent.mkdir(parents=True)
        pdf_path.write_bytes(_make_pdf('Governance institutions check executive power.'))

        cache.clear()
        url = '/media/articles/org/doc.pdf'
        first = get_attachment_text(url, 'doc.pdf')
        assert 'Governance' in first
        pdf_path.unlink()
        second = get_attachment_text(url, 'doc.pdf')
        assert second == first
