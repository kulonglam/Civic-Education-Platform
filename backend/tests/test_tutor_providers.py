import pytest

from apps.tutor.exceptions import TutorUnavailable
from apps.tutor.providers import (
    AnthropicTutorProvider,
    BaseTutorProvider,
    OpenAICompatibleTutorProvider,
    StubTutorProvider,
    get_tutor_provider,
    resolve_provider_name,
)
from apps.tutor.services import TutorService
from apps.tutor.sessions import get_session

QUESTION = 'What is a constitution?'
MESSAGES = [{'role': 'user', 'content': QUESTION}]


@pytest.fixture
def no_ai_credentials(settings):
    settings.TUTOR_PROVIDER = 'auto'
    settings.ANTHROPIC_API_KEY = ''
    settings.OPENAI_API_KEY = ''
    settings.OPENAI_BASE_URL = ''
    return settings


class TestProviderSelection:
    def test_auto_without_credentials_uses_stub(self, no_ai_credentials):
        assert resolve_provider_name() == 'stub'
        assert isinstance(get_tutor_provider(), StubTutorProvider)

    def test_auto_prefers_anthropic_over_openai(self, no_ai_credentials):
        no_ai_credentials.ANTHROPIC_API_KEY = 'sk-ant-test'
        no_ai_credentials.OPENAI_API_KEY = 'sk-openai-test'
        assert resolve_provider_name() == 'anthropic'
        assert isinstance(get_tutor_provider(), AnthropicTutorProvider)

    def test_auto_falls_back_to_openai(self, no_ai_credentials):
        no_ai_credentials.OPENAI_API_KEY = 'sk-openai-test'
        assert resolve_provider_name() == 'openai'
        assert isinstance(get_tutor_provider(), OpenAICompatibleTutorProvider)

    def test_base_url_alone_selects_openai(self, no_ai_credentials):
        """A local Ollama server needs no API key, only a base URL."""
        no_ai_credentials.OPENAI_BASE_URL = 'http://localhost:11434/v1'
        assert resolve_provider_name() == 'openai'

    def test_explicit_provider_is_honored(self, no_ai_credentials):
        no_ai_credentials.TUTOR_PROVIDER = 'anthropic'
        no_ai_credentials.ANTHROPIC_API_KEY = 'sk-ant-test'
        assert resolve_provider_name() == 'anthropic'

    def test_explicit_provider_without_credentials_degrades_to_stub(self, no_ai_credentials):
        no_ai_credentials.TUTOR_PROVIDER = 'anthropic'
        assert resolve_provider_name() == 'stub'

    def test_unknown_provider_degrades_to_stub(self, no_ai_credentials):
        no_ai_credentials.TUTOR_PROVIDER = 'gemini'
        assert resolve_provider_name() == 'stub'


class TestStubProvider:
    def test_complete_echoes_question_and_reports_zero_tokens(self):
        reply, tokens = StubTutorProvider().complete(system_prompt='ignored', messages=MESSAGES)
        assert tokens == 0
        assert QUESTION in reply

    def test_stream_yields_one_text_chunk(self):
        chunks = list(StubTutorProvider().stream(system_prompt='ignored', messages=MESSAGES))
        assert len(chunks) == 1
        text, tokens = chunks[0]
        assert tokens == 0
        assert QUESTION in text


class RecordingProvider(BaseTutorProvider):
    """Honors the (text, 0) deltas then ('', total_tokens) terminal contract."""

    name = 'recording'

    def complete(self, *, system_prompt, messages):
        return 'full reply', 42

    def stream(self, *, system_prompt, messages):
        yield 'Hello ', 0
        yield 'world', 0
        yield '', 99


class FailingProvider(BaseTutorProvider):
    name = 'failing'

    def complete(self, *, system_prompt, messages):
        raise TutorUnavailable()

    def stream(self, *, system_prompt, messages):
        raise TutorUnavailable()
        yield  # unreachable, but makes this a generator like the real providers


@pytest.mark.django_db
class TestServiceHonorsProviderContract:
    def test_chat_uses_provider_completion(self, org, citizen_user):
        result = TutorService(provider=RecordingProvider()).chat(citizen_user, 'Explain elections')
        assert result['reply'] == 'full reply'
        assert result['tokens_used'] == 42

    def test_stream_separates_text_deltas_from_the_token_total(self, org, citizen_user):
        events = list(TutorService(provider=RecordingProvider()).chat_stream(citizen_user, 'Explain elections'))

        assert [e['data']['text'] for e in events if e['event'] == 'token'] == ['Hello ', 'world']
        done = events[-1]
        assert done['event'] == 'done'
        assert done['data']['reply'] == 'Hello world'
        assert done['data']['tokens_used'] == 99

    def test_stream_failure_emits_error_and_rolls_back_the_user_message(self, org, citizen_user):
        events = list(TutorService(provider=FailingProvider()).chat_stream(citizen_user, 'Explain elections'))

        assert events[-1]['event'] == 'error'
        assert get_session(citizen_user)['messages'] == []
