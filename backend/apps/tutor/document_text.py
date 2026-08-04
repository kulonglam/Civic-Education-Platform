"""Extract searchable text from article PDF attachments for tutor retrieval."""

from __future__ import annotations

import hashlib
import logging
import re
from io import BytesIO
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

PDF_CACHE_TTL = 60 * 60 * 24  # 24 hours
PDF_FETCH_TIMEOUT = 30
MAX_PDF_BYTES = 20 * 1024 * 1024


def sanitize_text_for_db(text: str) -> str:
    """PostgreSQL text fields reject NUL (0x00) bytes; PDF extractors may emit them."""
    if not text:
        return ''
    return text.replace('\x00', '')


def extract_pdf_text(data: bytes) -> str:
    """Return plain text from PDF bytes; empty string on failure."""
    if not data or not data.lstrip().startswith(b'%PDF'):
        return ''
    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(data))
        parts: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ''
            if text.strip():
                parts.append(text)
        return sanitize_text_for_db(re.sub(r'\s+', ' ', ' '.join(parts)).strip())
    except Exception as exc:  # noqa: BLE001
        logger.warning('PDF text extraction failed: %s', exc)
        return ''


def _cache_key(attachment_url: str) -> str:
    digest = hashlib.sha256(attachment_url.encode()).hexdigest()[:32]
    return f'tutor:pdf-text:{digest}'


def _local_media_path(attachment_url: str) -> Path | None:
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    if not media_root:
        return None
    media_url = settings.MEDIA_URL.rstrip('/')
    url = attachment_url.strip()
    rel: str | None = None
    if media_url and media_url in url:
        rel = url.split(media_url, 1)[1].lstrip('/')
    elif '/media/' in url:
        rel = url.split('/media/', 1)[1].lstrip('/')
    elif url.startswith('articles/'):
        rel = url
    if not rel:
        return None
    path = Path(media_root) / rel.replace('/', '\\') if '\\' in str(media_root) else Path(media_root) / rel
    return path if path.is_file() else None


def fetch_attachment_bytes(attachment_url: str) -> bytes | None:
    """Load attachment bytes from local media or remote URL."""
    url = (attachment_url or '').strip()
    if not url:
        return None

    local_path = _local_media_path(url)
    if local_path is not None:
        try:
            data = local_path.read_bytes()
            return data if len(data) <= MAX_PDF_BYTES else None
        except OSError as exc:
            logger.warning('Could not read local attachment %s: %s', local_path, exc)

    if not url.startswith(('http://', 'https://')):
        return None

    try:
        from apps.core.safe_http import safe_urlopen

        request = Request(url, headers={'User-Agent': 'CivicEducationRSS-Tutor/1.0'})
        with safe_urlopen(request, timeout=PDF_FETCH_TIMEOUT, allow_http=True) as response:
            data = response.read(MAX_PDF_BYTES + 1)
            if len(data) > MAX_PDF_BYTES:
                logger.warning('Attachment too large for tutor extraction: %s', url)
                return None
            return data
    except (URLError, OSError, ValueError) as exc:
        logger.warning('Could not fetch attachment %s: %s', url, exc)
        return None


def invalidate_attachment_text_cache(attachment_url: str) -> None:
    """Drop cached PDF text when an article attachment changes."""
    url = (attachment_url or '').strip()
    if not url:
        return
    cache.delete(_cache_key(url))


def get_attachment_text(attachment_url: str, attachment_name: str = '') -> str:
    """Extract and cache PDF text for an article attachment."""
    url = (attachment_url or '').strip()
    if not url:
        return ''

    name = (attachment_name or '').lower()
    if not (name.endswith('.pdf') or url.lower().split('?', 1)[0].endswith('.pdf')):
        return ''

    cache_key = _cache_key(url)
    cached = cache.get(cache_key)
    if isinstance(cached, str):
        return cached

    data = fetch_attachment_bytes(url)
    if not data:
        cache.set(cache_key, '', timeout=300)
        return ''

    text = extract_pdf_text(data)
    cache.set(cache_key, text, timeout=PDF_CACHE_TTL if text else 300)
    return text
