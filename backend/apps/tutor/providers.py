"""Pluggable AI providers for the tutor.

Mirrors ``apps/billing/providers.py``: a base class, concrete implementations,
and a settings-driven factory.

The ``stub`` provider needs no credentials and returns a deterministic
development reply, so a fresh checkout and the test suite work with no API
keys. ``anthropic`` calls Claude. ``openai`` targets any OpenAI-compatible
chat-completions endpoint, which covers OpenAI itself, free local runtimes such
as Ollama, and gateways such as OpenRouter.

Every provider speaks the same two-method contract:

* ``complete()`` returns ``(text, total_tokens)``.
* ``stream()`` yields ``(text_delta, 0)`` per chunk and finishes with a single
  ``('', total_tokens)`` pair. Callers distinguish the two by checking the token
  slot first, so a text delta must never carry a non-zero token count.
"""

import logging
from collections.abc import Iterator

from django.conf import settings

from .exceptions import TutorUnavailable

logger = logging.getLogger(__name__)

DEFAULT_ANTHROPIC_MODEL = 'claude-sonnet-4-20250514'
DEFAULT_OPENAI_MODEL = 'gpt-4o-mini'
DEFAULT_MAX_TOKENS = 1024


def _last_user_message(messages: list[dict]) -> str:
    return next((m['content'] for m in reversed(messages) if m['role'] == 'user'), '')


class BaseTutorProvider:
    name = 'base'

    def complete(self, *, system_prompt: str, messages: list[dict]) -> tuple[str, int]:
        raise NotImplementedError

    def stream(self, *, system_prompt: str, messages: list[dict]) -> Iterator[tuple[str, int]]:
        raise NotImplementedError


class StubTutorProvider(BaseTutorProvider):
    """Offline provider used when no AI credentials are configured."""

    name = 'stub'

    def __init__(self, *, api_key=None, model=None, max_tokens=None, **kwargs):
        pass

    def _reply(self, messages: list[dict]) -> str:
        return (
            'This is a development response (no AI provider configured). '
            f'You asked: "{_last_user_message(messages)[:200]}". '
            'In production, the configured model will provide multilingual '
            'civic education guidance here.'
        )

    def complete(self, *, system_prompt: str, messages: list[dict]) -> tuple[str, int]:
        return self._reply(messages), 0

    def stream(self, *, system_prompt: str, messages: list[dict]) -> Iterator[tuple[str, int]]:
        yield self._reply(messages), 0


class AnthropicTutorProvider(BaseTutorProvider):
    name = 'anthropic'

    def __init__(self, *, api_key=None, model=None, max_tokens=None):
        self.api_key = api_key if api_key is not None else getattr(settings, 'ANTHROPIC_API_KEY', '')
        self.model = model or getattr(settings, 'ANTHROPIC_MODEL', DEFAULT_ANTHROPIC_MODEL)
        self.max_tokens = max_tokens or getattr(settings, 'ANTHROPIC_MAX_TOKENS', DEFAULT_MAX_TOKENS)

    def _client(self):
        import anthropic

        return anthropic.Anthropic(api_key=self.api_key)

    def complete(self, *, system_prompt: str, messages: list[dict]) -> tuple[str, int]:
        try:
            response = self._client().messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=messages,
            )
            text = ''.join(block.text for block in response.content if block.type == 'text')
            tokens = response.usage.input_tokens + response.usage.output_tokens
            return text.strip(), tokens
        except Exception as exc:  # noqa: BLE001
            logger.exception('Anthropic API call failed: %s', exc)
            raise TutorUnavailable() from exc

    def stream(self, *, system_prompt: str, messages: list[dict]) -> Iterator[tuple[str, int]]:
        try:
            with self._client().messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=messages,
            ) as stream:
                for event in stream:
                    if event.type == 'content_block_delta' and hasattr(event.delta, 'text'):
                        yield event.delta.text, 0
                final = stream.get_final_message()
                yield '', final.usage.input_tokens + final.usage.output_tokens
        except Exception as exc:  # noqa: BLE001
            logger.exception('Anthropic streaming call failed: %s', exc)
            raise TutorUnavailable() from exc


class OpenAICompatibleTutorProvider(BaseTutorProvider):
    """Any OpenAI-compatible endpoint: OpenAI, Ollama, OpenRouter, Groq, Together."""

    name = 'openai'

    def __init__(self, *, api_key=None, base_url=None, model=None, max_tokens=None):
        self.api_key = api_key if api_key is not None else getattr(settings, 'OPENAI_API_KEY', '')
        self.base_url = base_url if base_url is not None else getattr(settings, 'OPENAI_BASE_URL', '')
        self.model = model or getattr(settings, 'OPENAI_MODEL', DEFAULT_OPENAI_MODEL)
        self.max_tokens = max_tokens or getattr(settings, 'OPENAI_MAX_TOKENS', DEFAULT_MAX_TOKENS)

    def _client(self):
        from openai import OpenAI

        # Local runtimes such as Ollama ignore the key, but the SDK rejects a blank one.
        return OpenAI(api_key=self.api_key or 'not-needed', base_url=self.base_url or None)

    @staticmethod
    def _payload(system_prompt: str, messages: list[dict]) -> list[dict]:
        return [{'role': 'system', 'content': system_prompt}, *messages]

    @staticmethod
    def _token_total(usage) -> int:
        if usage is None:
            return 0
        return (getattr(usage, 'prompt_tokens', 0) or 0) + (getattr(usage, 'completion_tokens', 0) or 0)

    def complete(self, *, system_prompt: str, messages: list[dict]) -> tuple[str, int]:
        try:
            response = self._client().chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=self._payload(system_prompt, messages),
            )
            text = response.choices[0].message.content or ''
            return text.strip(), self._token_total(getattr(response, 'usage', None))
        except Exception as exc:  # noqa: BLE001
            logger.exception('OpenAI-compatible API call failed: %s', exc)
            raise TutorUnavailable() from exc

    def stream(self, *, system_prompt: str, messages: list[dict]) -> Iterator[tuple[str, int]]:
        try:
            # stream_options={'include_usage': True} would give exact token counts but is
            # rejected by several OpenAI-compatible servers, so usage is read only when a
            # server volunteers it and otherwise reported as 0.
            chunks = self._client().chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=self._payload(system_prompt, messages),
                stream=True,
            )
            tokens = 0
            for chunk in chunks:
                tokens = self._token_total(getattr(chunk, 'usage', None)) or tokens
                for choice in chunk.choices or []:
                    piece = getattr(choice.delta, 'content', None)
                    if piece:
                        yield piece, 0
            yield '', tokens
        except Exception as exc:  # noqa: BLE001
            logger.exception('OpenAI-compatible streaming call failed: %s', exc)
            raise TutorUnavailable() from exc


PROVIDERS: dict[str, type[BaseTutorProvider]] = {
    'stub': StubTutorProvider,
    'anthropic': AnthropicTutorProvider,
    'openai': OpenAICompatibleTutorProvider,
}


def _anthropic_configured() -> bool:
    return bool(getattr(settings, 'ANTHROPIC_API_KEY', ''))


def _openai_configured() -> bool:
    return bool(getattr(settings, 'OPENAI_API_KEY', '') or getattr(settings, 'OPENAI_BASE_URL', ''))


def resolve_provider_name() -> str:
    """Resolve the active provider, degrading to the stub when credentials are missing."""
    configured = (getattr(settings, 'TUTOR_PROVIDER', 'auto') or 'auto').strip().lower()

    if configured == 'auto':
        if _anthropic_configured():
            return 'anthropic'
        if _openai_configured():
            return 'openai'
        return 'stub'

    if configured not in PROVIDERS:
        logger.warning('Unknown TUTOR_PROVIDER %r — falling back to the stub provider.', configured)
        return 'stub'
    if configured == 'anthropic' and not _anthropic_configured():
        logger.warning('TUTOR_PROVIDER=anthropic but ANTHROPIC_API_KEY is unset — using the stub provider.')
        return 'stub'
    if configured == 'openai' and not _openai_configured():
        logger.warning(
            'TUTOR_PROVIDER=openai but neither OPENAI_API_KEY nor OPENAI_BASE_URL is set — '
            'using the stub provider.'
        )
        return 'stub'
    return configured


def get_tutor_provider(*, max_tokens=None) -> BaseTutorProvider:
    cls = PROVIDERS[resolve_provider_name()]
    if max_tokens is None:
        return cls()
    return cls(max_tokens=max_tokens)
