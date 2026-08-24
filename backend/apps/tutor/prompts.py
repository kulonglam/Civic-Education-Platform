"""System prompt construction for the AI tutor."""

from apps.core.branding import PLATFORM_NAME
from apps.core.constants import normalize_language
from apps.learning.models import Article
from apps.tenants.context import get_current_organization
from apps.tenants.services import get_user_organization

LANGUAGE_NAMES = {
    'en': 'English',
    'ar': 'Arabic',
}


def _user_language(user) -> str:
    profile = getattr(user, 'profile', None)
    if profile is not None:
        return normalize_language(profile.preferred_language)
    return 'en'


def build_system_prompt(
    user,
    article: Article | None,
    message: str = '',
    *,
    chunks: list[dict] | None = None,
) -> str:
    lang = _user_language(user)
    lang_name = LANGUAGE_NAMES.get(lang, 'English')
    org = get_current_organization() or get_user_organization(user)
    org_name = org.name if org else PLATFORM_NAME

    prompt = (
        'You are a civic education tutor for citizens of South Sudan on the '
        f'"{org_name}" platform. Answer clearly and accurately about democracy, '
        'constitutional rights, governance, elections, peacebuilding, and civic participation. '
        'The curriculum is organized in four categories: Constitution, Governance, Elections, '
        'and Peacebuilding. Prefer published platform materials (article text and PDF '
        'attachments) when provided below — especially the Transitional Constitution for '
        'constitutional questions. '
        'Use age-appropriate language. If unsure, say so rather than invent facts. '
        f'Reply in {lang_name}.'
    )
    if article is not None:
        prompt += (
            f'\n\nThe learner is reading this article titled "{article.title}":\n'
            f'{article.content[:3000]}'
        )

    from .retrieval import format_retrieved_context, retrieve_article_chunks

    if chunks is None:
        chunks = retrieve_article_chunks(
            message,
            exclude_article_id=article.pk if article is not None else None,
        )
    knowledge = format_retrieved_context(chunks)
    if knowledge:
        prompt += f'\n\n{knowledge}'
    return prompt


def build_api_messages(session: dict) -> list[dict]:
    return [{'role': m['role'], 'content': m['content']} for m in session['messages']]
