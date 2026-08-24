"""AI tutor orchestration.

Ties together the daily quota (:mod:`budget`), conversation state
(:mod:`sessions`), prompt construction (:mod:`prompts`) and the configured AI
backend (:mod:`providers`).

Names that moved into those modules are re-exported here so existing imports of
``apps.tutor.services`` keep working.
"""

from rest_framework.exceptions import ValidationError

from apps.learning.models import Article

from .budget import (
    DEFAULT_DAILY_LIMIT,
    enforce_budget,
    get_daily_limit,
    get_daily_usage,
    increment_daily_usage,
)
from .exceptions import TutorBudgetExceeded, TutorUnavailable
from .history import get_chat_session_history, list_chat_sessions
from .prompts import LANGUAGE_NAMES, build_api_messages, build_system_prompt
from .providers import BaseTutorProvider, get_tutor_provider
from .sessions import (
    SESSION_TTL,
    clear_session,
    get_active_session_payload,
    get_session,
    save_session,
)

__all__ = [
    'DEFAULT_DAILY_LIMIT',
    'LANGUAGE_NAMES',
    'SESSION_TTL',
    'TutorBudgetExceeded',
    'TutorService',
    'TutorUnavailable',
    'build_api_messages',
    'build_system_prompt',
    'clear_session',
    'enforce_budget',
    'get_active_session_payload',
    'get_chat_session_history',
    'get_daily_limit',
    'get_daily_usage',
    'get_session',
    'get_tutor_service',
    'increment_daily_usage',
    'list_chat_sessions',
    'save_session',
]


class TutorService:
    """Runs a tutor turn against whichever AI provider is configured."""

    def __init__(self, provider: BaseTutorProvider | None = None):
        self.provider = provider or get_tutor_provider()

    def chat(self, user, message: str, article_id=None) -> dict:
        message = message.strip()
        if not message:
            raise ValidationError({'message': 'Message cannot be empty.'})

        enforce_budget(user)

        article = None
        if article_id:
            article = Article.objects.filter(id=article_id, status='published').first()
            if article is None:
                raise ValidationError({'article_id': 'Article not found or not published.'})

        session = get_session(user)
        if article_id:
            session['article_id'] = str(article_id)

        session['messages'].append({'role': 'user', 'content': message})
        from .retrieval import retrieve_article_chunks, serialize_sources

        chunks = retrieve_article_chunks(
            message,
            exclude_article_id=article.pk if article is not None else None,
        )
        system_prompt = build_system_prompt(user, article, message, chunks=chunks)
        reply, tokens_used = self.provider.complete(
            system_prompt=system_prompt,
            messages=build_api_messages(session),
        )

        session['messages'].append({'role': 'assistant', 'content': reply})
        save_session(user, session)
        messages_used = increment_daily_usage(user)

        self._persist_messages(user, session, message, reply, tokens_used, article)

        limit = get_daily_limit(user)
        remaining = None if limit is None else max(limit - messages_used, 0)

        return {
            'session_id': session['session_id'],
            'reply': reply,
            'sources': serialize_sources(chunks),
            'tokens_used': tokens_used,
            'messages_used_today': messages_used,
            'daily_limit': limit,
            'messages_remaining': remaining,
        }

    def chat_stream(self, user, message: str, article_id=None):
        """Generator yielding SSE event dicts: token, done, or error."""
        message = message.strip()
        if not message:
            yield {'event': 'error', 'data': {'detail': 'Message cannot be empty.'}}
            return

        try:
            enforce_budget(user)
        except Exception as exc:  # noqa: BLE001
            yield {'event': 'error', 'data': {'detail': str(exc)}}
            return

        article = None
        if article_id:
            article = Article.objects.filter(id=article_id, status='published').first()
            if article is None:
                yield {'event': 'error', 'data': {'detail': 'Article not found or not published.'}}
                return

        session = get_session(user)
        if article_id:
            session['article_id'] = str(article_id)

        session['messages'].append({'role': 'user', 'content': message})
        from .retrieval import retrieve_article_chunks, serialize_sources

        chunks = retrieve_article_chunks(
            message,
            exclude_article_id=article.pk if article is not None else None,
        )
        system_prompt = build_system_prompt(user, article, message, chunks=chunks)

        reply_parts: list[str] = []
        tokens_used = 0
        try:
            for piece, token_hint in self.provider.stream(
                system_prompt=system_prompt,
                messages=build_api_messages(session),
            ):
                if token_hint:
                    tokens_used = token_hint
                elif piece:
                    reply_parts.append(piece)
                    yield {'event': 'token', 'data': {'text': piece}}
        except TutorUnavailable:
            yield {'event': 'error', 'data': {'detail': 'AI tutor is temporarily unavailable.'}}
            session['messages'].pop()
            save_session(user, session)
            return

        reply = ''.join(reply_parts).strip()
        session['messages'].append({'role': 'assistant', 'content': reply})
        save_session(user, session)
        messages_used = increment_daily_usage(user)
        self._persist_messages(user, session, message, reply, tokens_used, article)

        limit = get_daily_limit(user)
        remaining = None if limit is None else max(limit - messages_used, 0)

        yield {
            'event': 'done',
            'data': {
                'session_id': session['session_id'],
                'reply': reply,
                'sources': serialize_sources(chunks),
                'tokens_used': tokens_used,
                'messages_used_today': messages_used,
                'daily_limit': limit,
                'messages_remaining': remaining,
            },
        }

    @staticmethod
    def _persist_messages(user, session, user_message, assistant_message, tokens_used, article):
        from .tasks import persist_chat_messages_task

        persist_chat_messages_task.delay(
            str(user.pk),
            session['session_id'],
            user_message,
            assistant_message,
            tokens_used,
            str(article.pk) if article else None,
        )

    def usage_summary(self, user) -> dict:
        session = get_session(user)
        limit = get_daily_limit(user)
        used = get_daily_usage(user)
        remaining = None if limit is None else max(limit - used, 0)
        user_messages = sum(1 for m in session['messages'] if m['role'] == 'user')
        return {
            'daily_limit': limit,
            'messages_used_today': used,
            'messages_remaining': remaining,
            'session_message_count': user_messages,
        }


def get_tutor_service() -> TutorService:
    return TutorService()
