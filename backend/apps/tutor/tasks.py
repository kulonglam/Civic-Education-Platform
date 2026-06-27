from celery import shared_task

from .models import TutorChat


@shared_task
def persist_chat_messages_task(
    user_id: str,
    session_id: str,
    user_message: str,
    assistant_message: str,
    tokens_used: int,
    article_id: str | None = None,
):
    article_kwargs = {'article_id': article_id} if article_id else {}
    TutorChat.objects.create(
        user_id=user_id,
        session_id=session_id,
        role=TutorChat.ROLE_USER,
        message=user_message,
        **article_kwargs,
    )
    TutorChat.objects.create(
        user_id=user_id,
        session_id=session_id,
        role=TutorChat.ROLE_ASSISTANT,
        message=assistant_message,
        tokens_used=tokens_used,
        **article_kwargs,
    )
