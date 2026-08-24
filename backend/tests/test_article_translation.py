import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.learning.models import Article
from apps.learning.translation import (
    KIND_EN_TO_AR,
    apply_article_translation,
    chunk_markdown,
    detect_language,
    resolve_translation_job,
    source_fingerprint,
    translate_markdown,
)
from apps.tutor.exceptions import TutorUnavailable
from apps.tutor.providers import BaseTutorProvider, StubTutorProvider, get_tutor_provider


class PrefixProvider(BaseTutorProvider):
    """Returns the source text with a prefix so markdown structure is preserved."""

    name = 'prefix'

    def __init__(self, prefix='[ar] '):
        self.prefix = prefix
        self.calls = []

    def complete(self, *, system_prompt, messages):
        text = messages[-1]['content']
        self.calls.append(text)
        return f'{self.prefix}{text}', 1

    def stream(self, *, system_prompt, messages):
        yield from ()


class FailingProvider(BaseTutorProvider):
    name = 'failing'

    def complete(self, *, system_prompt, messages):
        raise TutorUnavailable()

    def stream(self, *, system_prompt, messages):
        raise TutorUnavailable()
        yield  # pragma: no cover


@pytest.fixture
def english_article(db, org, category, editor_user):
    return Article.objects.create(
        organization=org,
        category=category,
        author=editor_user,
        title='Civic rights in South Sudan',
        content='Citizens have the right to vote and to peaceful assembly.',
        status='draft',
    )


@pytest.mark.django_db
class TestLanguageDetection:
    def test_english_text(self):
        assert detect_language('The Transitional Constitution of South Sudan') == 'en'

    def test_arabic_text(self):
        assert detect_language('الدستور الانتقالي لجنوب السودان') == 'ar'

    def test_arabic_outnumbers_latin(self):
        assert detect_language('Article 1 المادة الأولى من الدستور') == 'ar'


@pytest.mark.django_db
class TestChunkMarkdown:
    def test_short_text_is_one_chunk(self):
        assert chunk_markdown('# Heading\n\nShort.', 3000) == ['# Heading\n\nShort.']

    def test_splits_on_blank_lines_and_preserves_heading(self):
        text = '# Rights\n\n' + ('alpha ' * 20) + '\n\n' + ('bravo ' * 20)
        chunks = chunk_markdown(text, 80)
        assert len(chunks) >= 2
        assert chunks[0].startswith('# Rights')


@pytest.mark.django_db
class TestTranslateMarkdown:
    def test_chunking_preserves_headings(self, settings):
        settings.TRANSLATION_CHUNK_CHARS = 80
        provider = PrefixProvider(prefix='[ar] ')
        text = '# Rights\n\n' + ('alpha ' * 20) + '\n\n' + ('bravo ' * 20)
        result = translate_markdown(text, source='en', target='ar', provider=provider)
        assert '# Rights' in result
        assert len(provider.calls) >= 2


@pytest.mark.django_db
class TestApplyArticleTranslation:
    def test_english_to_arabic_fills_ar_fields(self, english_article):
        provider = PrefixProvider(prefix='[ar] ')
        assert apply_article_translation(english_article, provider=provider) is True
        english_article.refresh_from_db()
        assert english_article.title_ar.startswith('[ar] ')
        assert 'Civic rights' in english_article.title_ar
        assert english_article.content_ar.startswith('[ar] ')
        assert english_article.source_language == 'en'
        assert english_article.translation_status == Article.TRANSLATION_MACHINE
        assert english_article.translated_at is not None
        assert english_article.translation_fingerprint == source_fingerprint(
            'Civic rights in South Sudan',
            'Citizens have the right to vote and to peaceful assembly.',
        )

    def test_arabic_to_english_fills_english_fields(self, org, category, editor_user):
        article = Article.objects.create(
            organization=org,
            category=category,
            author=editor_user,
            title='',
            content='',
            title_ar='حقوق المواطن',
            content_ar='للمواطنين حق التصويت والتجمع السلمي.',
            status='draft',
        )
        provider = PrefixProvider(prefix='[en] ')
        assert apply_article_translation(article, provider=provider) is True
        article.refresh_from_db()
        assert article.title.startswith('[en] ')
        assert 'حقوق المواطن' in article.title_ar
        assert article.content.startswith('[en] ')
        assert article.source_language == 'ar'
        assert article.translation_status == Article.TRANSLATION_MACHINE

    def test_arabic_typed_in_english_box_is_copied_then_translated(self, org, category, editor_user):
        article = Article.objects.create(
            organization=org,
            category=category,
            author=editor_user,
            title='حقوق المواطن',
            content='للمواطنين حق التصويت.',
            status='draft',
        )
        provider = PrefixProvider(prefix='[en] ')
        assert apply_article_translation(article, provider=provider) is True
        article.refresh_from_db()
        assert article.title_ar == 'حقوق المواطن'
        assert article.content_ar == 'للمواطنين حق التصويت.'
        assert article.title.startswith('[en] ')
        assert article.content.startswith('[en] ')
        assert article.source_language == 'ar'

    def test_unchanged_fingerprint_is_skipped(self, english_article):
        provider = PrefixProvider()
        apply_article_translation(english_article, provider=provider)
        calls_after_first = len(provider.calls)
        english_article.refresh_from_db()
        assert apply_article_translation(english_article, provider=provider) is False
        assert len(provider.calls) == calls_after_first

    def test_both_sides_filled_without_fingerprint_are_skipped(self, org, category, editor_user):
        article = Article.objects.create(
            organization=org,
            category=category,
            author=editor_user,
            title='The Constitution',
            title_ar='الدستور',
            content='English body',
            content_ar='النص العربي',
            status='published',
            published_at=timezone.now(),
        )
        provider = PrefixProvider()
        assert resolve_translation_job(article) is None
        assert apply_article_translation(article, provider=provider) is False
        article.refresh_from_db()
        assert article.title_ar == 'الدستور'
        assert article.content_ar == 'النص العربي'
        assert provider.calls == []

    def test_stub_provider_leaves_fields_blank(self, english_article, settings):
        settings.TUTOR_PROVIDER = 'stub'
        settings.ANTHROPIC_API_KEY = ''
        settings.OPENAI_API_KEY = ''
        settings.OPENAI_BASE_URL = ''
        assert apply_article_translation(english_article) is False
        english_article.refresh_from_db()
        assert english_article.title_ar == ''
        assert english_article.content_ar == ''
        assert english_article.translation_status == Article.TRANSLATION_NONE

    def test_provider_failure_sets_failed_and_keeps_source(self, english_article):
        original_title = english_article.title
        original_content = english_article.content
        with pytest.raises(TutorUnavailable):
            apply_article_translation(english_article, provider=FailingProvider())
        english_article.refresh_from_db()
        assert english_article.title == original_title
        assert english_article.content == original_content
        assert english_article.title_ar == ''
        assert english_article.translation_status == Article.TRANSLATION_FAILED

    def test_disabled_flag_skips(self, english_article, settings):
        settings.TRANSLATION_ENABLED = False
        provider = PrefixProvider()
        assert apply_article_translation(english_article, provider=provider) is False
        assert provider.calls == []


@pytest.mark.django_db
class TestTranslationJobResolution:
    def test_english_only_is_en_to_ar(self, english_article):
        job = resolve_translation_job(english_article)
        assert job is not None
        assert job.kind == KIND_EN_TO_AR
        assert job.source_language == 'en'


@pytest.mark.django_db
class TestProviderMaxTokens:
    def test_stub_accepts_max_tokens_kwarg(self, settings):
        settings.TUTOR_PROVIDER = 'stub'
        settings.ANTHROPIC_API_KEY = ''
        settings.OPENAI_API_KEY = ''
        settings.OPENAI_BASE_URL = ''
        provider = get_tutor_provider(max_tokens=4096)
        assert isinstance(provider, StubTutorProvider)
        reply, tokens = provider.complete(
            system_prompt='x',
            messages=[{'role': 'user', 'content': 'hello'}],
        )
        assert tokens == 0
        assert 'hello' in reply


@pytest.mark.django_db
class TestTranslateMissingCommand:
    def test_dry_run_lists_english_only_articles(self, english_article, capsys):
        call_command('translate_missing', '--dry-run')
        captured = capsys.readouterr()
        assert str(english_article.pk) in captured.out
        assert 'en_to_ar' in captured.out
        english_article.refresh_from_db()
        assert english_article.title_ar == ''
