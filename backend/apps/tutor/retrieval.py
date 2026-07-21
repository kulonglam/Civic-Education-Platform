"""Lightweight retrieval over published articles for the AI tutor.

Uses simple keyword overlap scoring — no external vector DB — so the tutor can
ground answers in long documents such as the Transitional Constitution.
"""

from __future__ import annotations

import re

from apps.learning.models import Article

CHUNK_SIZE = 1400
CHUNK_OVERLAP = 200
MAX_CHUNKS = 5
MAX_CONTEXT_CHARS = 9000

_TOKEN_RE = re.compile(r"[a-zA-Z\u0600-\u06FF0-9']{3,}")


def _tokenize(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text or '')}


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    cleaned = re.sub(r'\s+', ' ', (text or '').strip())
    if not cleaned:
        return []
    if len(cleaned) <= size:
        return [cleaned]
    chunks: list[str] = []
    start = 0
    length = len(cleaned)
    while start < length:
        end = min(start + size, length)
        # Prefer breaking on sentence boundaries near the window end.
        if end < length:
            window = cleaned[start:end]
            for sep in ('. ', '; ', '\n'):
                idx = window.rfind(sep)
                if idx > size // 3:
                    end = start + idx + len(sep)
                    break
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= length:
            break
        start = max(end - overlap, start + 1)
    return chunks


def score_chunk(chunk: str, query_tokens: set[str]) -> float:
    if not query_tokens:
        return 0.0
    chunk_tokens = _tokenize(chunk)
    if not chunk_tokens:
        return 0.0
    overlap = query_tokens & chunk_tokens
    if not overlap:
        return 0.0
    # Reward denser matches; slight boost for longer informative chunks.
    density = len(overlap) / max(len(query_tokens), 1)
    return len(overlap) + density * 2.0


def retrieve_article_chunks(
    query: str,
    *,
    exclude_article_id=None,
    max_chunks: int = MAX_CHUNKS,
) -> list[dict]:
    """Return top-scoring chunks from published tenant articles.

    Controlled documents and constitution-category articles are boosted so the
    Transitional Constitution is preferred for civic questions.
    """
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    articles = (
        Article.objects.filter(status='published')
        .select_related('category')
        .only(
            'id',
            'title',
            'content',
            'is_controlled_document',
            'document_label',
            'category_id',
            'category__slug',
            'category__name',
        )
    )

    scored: list[tuple[float, dict]] = []
    for article in articles.iterator(chunk_size=50):
        if exclude_article_id and str(article.id) == str(exclude_article_id):
            continue
        body = (article.content or '').strip()
        if len(body) < 80:
            continue

        boost = 0.0
        if article.is_controlled_document:
            boost += 3.0
        slug = getattr(article.category, 'slug', '') or ''
        if slug == 'constitution':
            boost += 2.0
        label = (article.document_label or article.title or '').lower()
        if 'constitution' in label:
            boost += 1.5

        source = article.document_label or article.title
        for chunk in chunk_text(body):
            raw = score_chunk(chunk, query_tokens)
            if raw <= 0:
                continue
            scored.append(
                (
                    raw + boost,
                    {
                        'source': source,
                        'title': article.title,
                        'text': chunk,
                        'score': raw + boost,
                    },
                )
            )

    scored.sort(key=lambda item: item[0], reverse=True)

    selected: list[dict] = []
    total_chars = 0
    for _, item in scored:
        if len(selected) >= max_chunks:
            break
        if total_chars + len(item['text']) > MAX_CONTEXT_CHARS:
            continue
        selected.append(item)
        total_chars += len(item['text'])
    return selected


def format_retrieved_context(chunks: list[dict]) -> str:
    if not chunks:
        return ''
    parts = [
        'Use the following excerpts from platform learning materials when relevant. '
        'Cite the source document by name when you rely on them. '
        'If the excerpts do not cover the question, say what is missing rather than inventing text.'
    ]
    for i, chunk in enumerate(chunks, start=1):
        parts.append(f'\n[{i}] Source: {chunk["source"]}\n{chunk["text"]}')
    return '\n'.join(parts)
