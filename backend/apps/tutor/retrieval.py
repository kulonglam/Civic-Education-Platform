"""Lightweight retrieval over published articles for the AI tutor.

Uses keyword overlap scoring over article body text and PDF attachments — no
external vector DB — so the tutor can ground answers in long documents such as
the Transitional Constitution across all four civic categories.
"""

from __future__ import annotations

import re

from apps.learning.models import Article

from .document_text import get_attachment_text

CHUNK_SIZE = 1400
CHUNK_OVERLAP = 200
MAX_CHUNKS = 6
MAX_CONTEXT_CHARS = 9000
MIN_SEARCHABLE_CHARS = 40

# Official curriculum categories seeded for the platform.
CATEGORY_SLUGS = ('constitution', 'governance', 'elections', 'peacebuilding')

CATEGORY_LABELS = {
    'constitution': 'Constitution',
    'governance': 'Governance',
    'elections': 'Elections',
    'peacebuilding': 'Peacebuilding',
}

# Keywords (EN + AR fragments) used to infer which category a question targets.
CATEGORY_KEYWORDS: dict[str, set[str]] = {
    'constitution': {
        'constitution', 'constitutional', 'article', 'articles', 'rights', 'bill',
        'fundamental', 'law', 'laws', 'court', 'courts', 'judiciary', 'legal',
        'transitional', 'amendment', 'chapter', 'part', 'equality', 'freedom',
        'دستور', 'حق', 'حقوق', 'مادة', 'قانون',
    },
    'governance': {
        'governance', 'government', 'govern', 'local', 'state', 'states', 'county',
        'counties', 'institution', 'institutions', 'minister', 'ministry',
        'parliament', 'legislature', 'legislative', 'executive', 'cabinet',
        'administration', 'public', 'service', 'services', 'decentral',
        'حكم', 'حكومة', 'محلي', 'ولاية', 'مجلس',
    },
    'elections': {
        'election', 'elections', 'elect', 'vote', 'voting', 'voter', 'voters',
        'ballot', 'ballots', 'candidate', 'candidates', 'campaign', 'poll',
        'polls', 'referendum', 'turnout', 'register', 'registration', 'nomination',
        'انتخاب', 'انتخابات', 'تصويت', 'ناخب',
    },
    'peacebuilding': {
        'peace', 'peacebuilding', 'reconciliation', 'conflict', 'unity', 'dialogue',
        'security', 'violence', 'disarm', 'community', 'trust', 'mediation',
        'tolerance', 'coexist', 'national', 'healing', 'سلام', 'مصالحة', 'نزاع',
    },
}

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
    density = len(overlap) / max(len(query_tokens), 1)
    return len(overlap) + density * 2.0


def detect_query_categories(query_tokens: set[str]) -> set[str]:
    """Return category slugs that match terms in the user's question."""
    if not query_tokens:
        return set()
    matched: set[str] = set()
    for slug, keywords in CATEGORY_KEYWORDS.items():
        if query_tokens & keywords:
            matched.add(slug)
    return matched


def _category_boost(category_slug: str, query_categories: set[str]) -> float:
    boost = 0.0
    if category_slug in CATEGORY_SLUGS:
        boost += 0.5
    if category_slug in query_categories:
        boost += 4.0
    if category_slug == 'constitution':
        boost += 0.5
    return boost


def _article_searchable_text(article: Article) -> tuple[str, str]:
    """Combine article body and PDF attachment text for retrieval.

    Returns (searchable_text, source_kind) where source_kind is 'text', 'pdf',
    or 'text+pdf' for logging/context hints.
    """
    indexed = (getattr(article, 'tutor_index_text', None) or '').strip()
    if len(indexed) >= MIN_SEARCHABLE_CHARS:
        body = (article.content or '').strip()
        has_pdf = bool(article.attachment_url)
        if has_pdf and len(indexed) > len(body) + 100:
            return indexed, 'text+pdf' if body else 'pdf'
        return indexed, 'text'

    body = (article.content or '').strip()
    pdf_text = ''
    if article.attachment_url:
        pdf_text = get_attachment_text(article.attachment_url, article.attachment_name or '')

    if not pdf_text:
        return body, 'text'

    if len(body) < 400:
        return pdf_text if len(pdf_text) > len(body) else (body + '\n\n' + pdf_text), 'text+pdf'

    body_tokens = _tokenize(body)
    pdf_tokens = _tokenize(pdf_text)
    novel_pdf_tokens = pdf_tokens - body_tokens
    if len(novel_pdf_tokens) > 25:
        return body + '\n\n' + pdf_text, 'text+pdf'
    return body, 'text'


def retrieve_article_chunks(
    query: str,
    *,
    exclude_article_id=None,
    max_chunks: int = MAX_CHUNKS,
) -> list[dict]:
    """Return top-scoring chunks from published tenant articles (text + PDF).

    Controlled documents and category-matched articles are boosted so answers
    stay accurate across Constitution, Governance, Elections, and Peacebuilding.
    """
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    query_categories = detect_query_categories(query_tokens)

    articles = (
        Article.objects.filter(status='published')
        .select_related('category')
        .only(
            'id',
            'title',
            'content',
            'tutor_index_text',
            'attachment_url',
            'attachment_name',
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

        searchable, source_kind = _article_searchable_text(article)
        if len(searchable) < MIN_SEARCHABLE_CHARS:
            continue

        category_slug = getattr(article.category, 'slug', '') or ''
        category_name = CATEGORY_LABELS.get(category_slug) or getattr(
            article.category, 'name', 'Learning material'
        )

        boost = _category_boost(category_slug, query_categories)
        if article.is_controlled_document:
            boost += 3.0
        if category_slug == 'constitution' and (
            query_categories & {'constitution'} or 'constitution' in query_tokens
        ):
            boost += 2.0
        label = (article.document_label or article.title or '').lower()
        if 'constitution' in label:
            boost += 1.5

        source = article.document_label or article.title
        display_source = f'{source} ({category_name})'
        if source_kind == 'pdf':
            display_source += ' [PDF]'
        elif source_kind == 'text+pdf':
            display_source += ' [text + PDF]'

        for chunk in chunk_text(searchable):
            raw = score_chunk(chunk, query_tokens)
            if raw <= 0:
                continue
            scored.append(
                (
                    raw + boost,
                    {
                        'source': display_source,
                        'article_id': str(article.id),
                        'title': article.title,
                        'category': category_name,
                        'category_slug': category_slug,
                        'text': chunk,
                        'score': raw + boost,
                        'source_kind': source_kind,
                    },
                )
            )

    scored.sort(key=lambda item: item[0], reverse=True)

    selected: list[dict] = []
    total_chars = 0
    seen_categories: set[str] = set()
    selected_keys: set[str] = set()

    def _chunk_key(item: dict) -> str:
        return f"{item.get('title', '')}:{item['text'][:80]}"

    for _, item in scored:
        if len(selected) >= max_chunks:
            break
        key = _chunk_key(item)
        if key in selected_keys:
            continue
        if total_chars + len(item['text']) > MAX_CONTEXT_CHARS:
            continue
        selected.append(item)
        selected_keys.add(key)
        total_chars += len(item['text'])
        if item.get('category_slug'):
            seen_categories.add(item['category_slug'])

    # Ensure breadth across categories when the query is general (no category hit).
    if not query_categories and len(seen_categories) < 2:
        for _, item in scored:
            if len(selected) >= max_chunks:
                break
            slug = item.get('category_slug') or ''
            if slug in seen_categories or slug not in CATEGORY_SLUGS:
                continue
            key = _chunk_key(item)
            if key in selected_keys:
                continue
            if total_chars + len(item['text']) > MAX_CONTEXT_CHARS:
                continue
            selected.append(item)
            selected_keys.add(key)
            total_chars += len(item['text'])
            seen_categories.add(slug)

    return selected


def format_retrieved_context(chunks: list[dict]) -> str:
    if not chunks:
        return ''
    parts = [
        'Use the following excerpts from platform learning materials when relevant. '
        'Materials are organized in four categories: Constitution, Governance, Elections, '
        'and Peacebuilding. Excerpts may come from article text and/or PDF attachments. '
        'Cite the source document and category when you rely on them. '
        'If the excerpts do not cover the question, say what is missing rather than inventing text.'
    ]
    for i, chunk in enumerate(chunks, start=1):
        parts.append(f'\n[{i}] Source: {chunk["source"]}\n{chunk["text"]}')
    return '\n'.join(parts)


def serialize_sources(chunks: list[dict]) -> list[dict]:
    """Deduplicate retrieved chunks into citation cards for the API response."""
    seen: set[str] = set()
    sources: list[dict] = []
    for chunk in chunks:
        key = chunk.get('source') or chunk.get('title') or ''
        if key in seen:
            continue
        seen.add(key)
        sources.append({
            'article_id': chunk.get('article_id'),
            'title': chunk.get('title', ''),
            'source': chunk.get('source', ''),
            'category': chunk.get('category', ''),
            'category_slug': chunk.get('category_slug', ''),
            'source_kind': chunk.get('source_kind', 'text'),
            'excerpt': (chunk.get('text') or '')[:280],
        })
    return sources
