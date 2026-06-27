"""HTML sanitization helpers (defense-in-depth for user-generated content)."""

import bleach

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'b', 'i', 'u', 'ul', 'ol', 'li', 'a',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'code', 'pre', 'hr',
]
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel', 'target'],
    '*': ['class'],
}


def sanitize_html(html: str) -> str:
    """Strip dangerous markup while preserving safe article formatting."""
    if not html:
        return ''
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )


def reject_dangerous_markdown(text: str) -> None:
    """Raise ValueError if raw markdown contains obvious XSS payloads."""
    if not text:
        return
    lowered = text.lower()
    blocked = ('<script', 'javascript:', 'onerror=', 'onload=', '<iframe', 'data:text/html')
    for needle in blocked:
        if needle in lowered:
            raise ValueError(f'Content contains disallowed pattern: {needle}')
