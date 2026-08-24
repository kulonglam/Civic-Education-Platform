"""Short-lived tutor conversation state held in the cache."""

import json
import uuid

from django.core.cache import cache

SESSION_TTL = 60 * 60


def _session_cache_key(user_id) -> str:
    return f'tutor:session:{user_id}'


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


def get_active_session_payload(user) -> dict:
    session = get_session(user)
    return {
        'session_id': session['session_id'],
        'article_id': session.get('article_id'),
        'messages': session.get('messages', []),
    }
