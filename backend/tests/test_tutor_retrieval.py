import pytest

from apps.learning.models import Article, Category
from apps.tutor.retrieval import chunk_text, format_retrieved_context, retrieve_article_chunks
from apps.tenants.context import set_current_organization


@pytest.mark.django_db
class TestTutorRetrieval:
    def test_chunk_text_splits_long_document(self):
        text = ('Article 14. Equality before the law. ' * 80).strip()
        chunks = chunk_text(text, size=200, overlap=40)
        assert len(chunks) > 1
        assert all(len(c) <= 240 for c in chunks)

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
