"""Read access to persisted tutor conversations."""

from .models import TutorChat


def list_chat_sessions(user, *, limit: int = 20) -> list[dict]:
    """Summarize recent tutor conversations persisted for the user."""
    from django.db.models import Count, Max, Min, Q

    rows = (
        TutorChat.objects.filter(user=user)
        .values('session_id')
        .annotate(
            started_at=Min('created_at'),
            last_at=Max('created_at'),
            turns=Count('id', filter=Q(role=TutorChat.ROLE_USER)),
        )
        .filter(turns__gt=0)
        .order_by('-last_at')[:limit]
    )

    sessions: list[dict] = []
    for row in rows:
        preview_row = (
            TutorChat.objects.filter(
                user=user,
                session_id=row['session_id'],
                role=TutorChat.ROLE_USER,
            )
            .order_by('created_at')
            .values('message', 'article_id')
            .first()
        )
        sessions.append({
            'session_id': row['session_id'],
            'preview': (preview_row['message'] if preview_row else '')[:120],
            'turns': row['turns'],
            'started_at': row['started_at'],
            'last_at': row['last_at'],
            'article_id': str(preview_row['article_id']) if preview_row and preview_row['article_id'] else None,
        })
    return sessions


def get_chat_session_history(user, session_id: str) -> dict | None:
    """Return ordered messages for a persisted session owned by the user."""
    rows = TutorChat.objects.filter(user=user, session_id=session_id).order_by('created_at')
    if not rows.exists():
        return None

    article_id = (
        rows.filter(article_id__isnull=False)
        .values_list('article_id', flat=True)
        .first()
    )
    return {
        'session_id': session_id,
        'article_id': str(article_id) if article_id else None,
        'messages': [{'role': row.role, 'content': row.message} for row in rows],
    }
