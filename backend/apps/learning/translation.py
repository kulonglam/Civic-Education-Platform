"""Automatic English/Arabic translation for civic-education articles.

Detects the author language from Unicode script (no API call), chunks
markdown on paragraph boundaries, and translates via the same pluggable
provider used by the AI tutor. The stub provider is never written into
article fields.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone

from apps.tutor.exceptions import TutorUnavailable
from apps.tutor.providers import get_tutor_provider, resolve_provider_name

logger = logging.getLogger(__name__)

KIND_EN_TO_AR = 'en_to_ar'
KIND_AR_TO_EN = 'ar_to_en'
KIND_RELOCATE_AR_THEN_EN = 'relocate_ar_then_en'

LANGUAGE_NAMES = {
    'en': 'English',
    'ar': 'Arabic',
}

# Arabic, Arabic Supplement, Arabic Extended-A/B, presentation forms.
_ARABIC_RANGES = (
    (0x0600, 0x06FF),
    (0x0750, 0x077F),
    (0x08A0, 0x08FF),
    (0x0870, 0x089F),
    (0xFB50, 0xFDFF),
    (0xFE70, 0xFEFF),
)

_SYSTEM_PROMPT = (
    'You are a professional translator for civic education materials about '
    'South Sudan (constitution, governance, elections, and peacebuilding). '
    'Translate the following markdown from {source} into {target}. '
    'Preserve markdown structure, headings, lists, links, URLs, and proper nouns. '
    'Return only the translated text — no preamble, no quotes, no commentary.'
)

_PARAGRAPH_SPLIT = re.compile(r'\n\s*\n')


@dataclass(frozen=True)
class TranslationJob:
    kind: str
    source_language: str
    source_title: str
    source_content: str


def _is_blank(value: str | None) -> bool:
    return not (value or '').strip()


def detect_language(text: str) -> str:
    """Return ``ar`` when Arabic letters outnumber Latin letters, else ``en``."""
    arabic = 0
    latin = 0
    for char in text or '':
        code = ord(char)
        if any(start <= code <= end for start, end in _ARABIC_RANGES):
            arabic += 1
        elif char.isalpha() and code < 0x0300:
            latin += 1
    if arabic > latin:
        return 'ar'
    return 'en'


def source_fingerprint(title: str, content: str) -> str:
    payload = f'{title or ""}\n{content or ""}'.encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def chunk_markdown(text: str, max_chars: int) -> list[str]:
    """Split on blank-line paragraph boundaries, keeping chunks under max_chars."""
    if max_chars <= 0 or len(text) <= max_chars:
        return [text] if text else []
    paragraphs = _PARAGRAPH_SPLIT.split(text)
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for para in paragraphs:
        extra = len(para) + (2 if current else 0)
        if current and current_len + extra > max_chars:
            chunks.append('\n\n'.join(current))
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += extra
    if current:
        chunks.append('\n\n'.join(current))
    return chunks


def resolve_translation_job(article) -> TranslationJob | None:
    """Decide what to translate, or ``None`` when there is nothing to do."""
    title = article.title or ''
    content = article.content or ''
    title_ar = article.title_ar or ''
    content_ar = article.content_ar or ''

    en_blank = _is_blank(title) and _is_blank(content)
    ar_blank = _is_blank(title_ar) and _is_blank(content_ar)

    if en_blank and ar_blank:
        return None

    if not en_blank and not ar_blank:
        source_lang = (article.source_language or '').strip()
        if source_lang == 'en':
            return TranslationJob(KIND_EN_TO_AR, 'en', title, content)
        if source_lang == 'ar':
            return TranslationJob(KIND_AR_TO_EN, 'ar', title_ar, content_ar)
        return None

    if not en_blank and ar_blank:
        detected = detect_language(f'{title}\n{content}')
        if detected == 'ar':
            return TranslationJob(KIND_RELOCATE_AR_THEN_EN, 'ar', title, content)
        return TranslationJob(KIND_EN_TO_AR, 'en', title, content)

    return TranslationJob(KIND_AR_TO_EN, 'ar', title_ar, content_ar)


def translate_markdown(
    text: str,
    *,
    source: str,
    target: str,
    provider,
) -> str:
    """Translate ``text`` from ``source`` to ``target`` using ``provider.complete()``."""
    if not (text or '').strip():
        return text or ''

    max_chars = int(getattr(settings, 'TRANSLATION_CHUNK_CHARS', 3000) or 3000)
    chunks = chunk_markdown(text, max_chars)
    system_prompt = _SYSTEM_PROMPT.format(
        source=LANGUAGE_NAMES.get(source, source),
        target=LANGUAGE_NAMES.get(target, target),
    )
    translated: list[str] = []
    for chunk in chunks:
        reply, _tokens = provider.complete(
            system_prompt=system_prompt,
            messages=[{'role': 'user', 'content': chunk}],
        )
        translated.append((reply or '').strip())
    return '\n\n'.join(part for part in translated if part)


def _truncate_title(value: str) -> str:
    return (value or '')[:255]


def _translation_provider(provider=None):
    if provider is not None:
        return provider
    max_tokens = int(getattr(settings, 'TRANSLATION_MAX_TOKENS', 4096) or 4096)
    return get_tutor_provider(max_tokens=max_tokens)


def apply_article_translation(article, *, provider=None) -> bool:
    """Fill the missing language side. Returns True when a write happened."""
    if not getattr(settings, 'TRANSLATION_ENABLED', True):
        return False

    from .models import Article
    from .tutor_index import build_tutor_index_text

    job = resolve_translation_job(article)
    if job is None:
        return False

    fingerprint = source_fingerprint(job.source_title, job.source_content)
    if fingerprint and fingerprint == (article.translation_fingerprint or ''):
        return False

    if provider is None and resolve_provider_name() == 'stub':
        logger.info('Skipping article translation for %s — stub provider is configured', article.pk)
        return False

    active_provider = _translation_provider(provider)

    try:
        updates = _build_updates(job, active_provider)
    except TutorUnavailable:
        Article.all_objects.filter(pk=article.pk).update(
            translation_status=Article.TRANSLATION_FAILED,
        )
        article.translation_status = Article.TRANSLATION_FAILED
        raise

    updates['source_language'] = job.source_language
    updates['translation_status'] = Article.TRANSLATION_MACHINE
    updates['translated_at'] = timezone.now()
    updates['translation_fingerprint'] = fingerprint

    for field, value in updates.items():
        setattr(article, field, value)
    if 'title' in updates or 'content' in updates:
        updates['tutor_index_text'] = build_tutor_index_text(article)

    Article.all_objects.filter(pk=article.pk).update(**updates)
    return True


def _build_updates(job: TranslationJob, provider) -> dict:
    if job.kind == KIND_RELOCATE_AR_THEN_EN:
        return {
            'title_ar': _truncate_title(job.source_title),
            'content_ar': job.source_content or '',
            'title': _truncate_title(
                translate_markdown(
                    job.source_title, source='ar', target='en', provider=provider,
                )
            ),
            'content': translate_markdown(
                job.source_content, source='ar', target='en', provider=provider,
            ),
        }
    if job.kind == KIND_EN_TO_AR:
        return {
            'title_ar': _truncate_title(
                translate_markdown(
                    job.source_title, source='en', target='ar', provider=provider,
                )
            ),
            'content_ar': translate_markdown(
                job.source_content, source='en', target='ar', provider=provider,
            ),
        }
    if job.kind == KIND_AR_TO_EN:
        return {
            'title': _truncate_title(
                translate_markdown(
                    job.source_title, source='ar', target='en', provider=provider,
                )
            ),
            'content': translate_markdown(
                job.source_content, source='ar', target='en', provider=provider,
            ),
        }
    raise ValueError(f'Unknown translation job kind: {job.kind}')
