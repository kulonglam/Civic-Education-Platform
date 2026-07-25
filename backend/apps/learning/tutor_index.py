"""Build and maintain pre-indexed tutor search text on articles."""

from __future__ import annotations

from apps.tutor.document_text import get_attachment_text


def build_tutor_index_text(article) -> str:
    """Combine article body and PDF attachment text for tutor retrieval."""
    parts: list[str] = []
    body = (article.content or '').strip()
    if body:
        parts.append(body)
    if article.attachment_url:
        pdf_text = get_attachment_text(article.attachment_url, article.attachment_name or '')
        if pdf_text:
            parts.append(pdf_text)
    return '\n\n'.join(parts).strip()
