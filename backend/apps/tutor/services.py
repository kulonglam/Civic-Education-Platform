import json
import logging
import uuid
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from rest_framework.exceptions import APIException, ValidationError

from apps.billing.services import get_active_plan
from apps.core.constants import normalize_language
from apps.learning.models import Article
from apps.tenants.context import get_current_organization
from apps.tenants.services import get_user_organization

from .models import TutorChat, TutorDailyUsage

logger = logging.getLogger(__name__)

SESSION_TTL = 60 * 60
DEFAULT_DAILY_LIMIT = 30

LANGUAGE_NAMES = {
    'en': 'English',
    'ar': 'Arabic',
}


class TutorBudgetExceeded(APIException):
    status_code = 429
    default_detail = 'Daily AI tutor message limit reached. Upgrade your plan for more messages.'
    default_code = 'tutor_budget_exceeded'


class TutorUnavailable(APIException):
    status_code = 503
    default_detail = 'AI tutor is temporarily unavailable.'
    default_code = 'tutor_unavailable'


def _session_cache_key(user_id) -> str:
    return f'tutor:session:{user_id}'


def _daily_cache_key(user_id) -> str:
    today = timezone.localdate().isoformat()
    return f'tutor:daily:{user_id}:{today}'


def _seconds_until_midnight() -> int:
    now = timezone.localtime()
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(int((tomorrow - now).total_seconds()), 60)


def get_daily_limit(user) -> int | None:
    organization = get_current_organization() or get_user_organization(user)
    plan = get_active_plan(organization) if organization else None
    if plan is None:
        return DEFAULT_DAILY_LIMIT
    limit = (plan.features or {}).get('tutor_daily_messages', DEFAULT_DAILY_LIMIT)
    if limit in (None, '', 'unlimited'):
        return None
    return int(limit)


def get_daily_usage(user) -> int:
    """Return today's usage from Redis cache, seeding from DB on cold miss."""
    key = _daily_cache_key(user.pk)
    cached = cache.get(key)
    if cached is not None:
        return int(cached)
    # Cold miss: read from DB to avoid double-counting across restarts
    today = timezone.localdate()
    row = TutorDailyUsage.objects.filter(user=user, date=today).first()
    count = row.message_count if row else 0
    cache.set(key, count, timeout=_seconds_until_midnight())
    return count


def increment_daily_usage(user) -> int:
    """Increment Redis counter and persist to DB asynchronously."""
    key = _daily_cache_key(user.pk)
    try:
        new_val = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=_seconds_until_midnight())
        new_val = 1
    # Write-through to DB using upsert so the counter survives cache eviction
    today = timezone.localdate()
    TutorDailyUsage.objects.update_or_create(
        user=user,
        date=today,
        defaults={'message_count': new_val},
    )
    return new_val


def enforce_budget(user) -> None:
    limit = get_daily_limit(user)
    if limit is None:
        return
    if get_daily_usage(user) >= limit:
        raise TutorBudgetExceeded(
            detail=f'Daily limit of {limit} tutor messages reached. Try again tomorrow or upgrade your plan.'
        )


def get_session(user) -> dict:
    raw = cache.get(_session_cache_key(user.pk))
    if not raw:
        return {
            'session_id': uuid.uuid4().hex,
            'messages': [],
            'article_id': None,
        }
    if isinstance(raw, str):
        return json.loads(raw)
    return raw


def save_session(user, session: dict) -> None:
    cache.set(_session_cache_key(user.pk), json.dumps(session), timeout=SESSION_TTL)


def clear_session(user) -> None:
    cache.delete(_session_cache_key(user.pk))


def _user_language(user) -> str:
    profile = getattr(user, 'profile', None)
    if profile is not None:
        return normalize_language(profile.preferred_language)
    return 'en'


def _build_system_prompt(user, article: Article | None, message: str = '') -> str:
    lang = _user_language(user)
    lang_name = LANGUAGE_NAMES.get(lang, 'English')
    org = get_current_organization() or get_user_organization(user)
    org_name = org.name if org else 'Civic Education Platform'

    prompt = (
        'You are a civic education tutor for citizens of South Sudan on the '
        f'"{org_name}" platform. Answer clearly and accurately about democracy, '
        'constitutional rights, governance, elections, peacebuilding, and civic participation. '
        'Prefer the Transitional Constitution of the Republic of South Sudan and other '
        'platform learning materials when they are provided below. '
        'Use age-appropriate language. If unsure, say so rather than invent facts. '
        f'Reply in {lang_name}.'
    )
    if article is not None:
        prompt += (
            f'\n\nThe learner is reading this article titled "{article.title}":\n'
            f'{article.content[:3000]}'
        )

    from .retrieval import format_retrieved_context, retrieve_article_chunks

    chunks = retrieve_article_chunks(
        message,
        exclude_article_id=article.pk if article is not None else None,
    )
    knowledge = format_retrieved_context(chunks)
    if knowledge:
        prompt += f'\n\n{knowledge}'
    return prompt


def _build_api_messages(session: dict) -> list[dict]:
    return [{'role': m['role'], 'content': m['content']} for m in session['messages']]


def _call_claude(*, system_prompt: str, messages: list[dict]) -> tuple[str, int]:
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    model = getattr(settings, 'ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')

    if not api_key:
        last_user = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), '')
        reply = (
            'This is a development response (no Anthropic API key configured). '
            f'You asked: "{last_user[:200]}". '
            'In production, Claude will provide multilingual civic education guidance here.'
        )
        return reply, 0

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=getattr(settings, 'ANTHROPIC_MAX_TOKENS', 1024),
            system=system_prompt,
            messages=messages,
        )
        text = ''.join(block.text for block in response.content if block.type == 'text')
        tokens = response.usage.input_tokens + response.usage.output_tokens
        return text.strip(), tokens
    except Exception as exc:  # noqa: BLE001
        logger.exception('Anthropic API call failed: %s', exc)
        raise TutorUnavailable() from exc


class ClaudeTutorService:
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
        system_prompt = _build_system_prompt(user, article, message)
        reply, tokens_used = _call_claude(
            system_prompt=system_prompt,
            messages=_build_api_messages(session),
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
            'tokens_used': tokens_used,
            'messages_used_today': messages_used,
            'daily_limit': limit,
            'messages_remaining': remaining,
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


def get_tutor_service() -> ClaudeTutorService:
    return ClaudeTutorService()
