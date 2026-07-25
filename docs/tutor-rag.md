# AI Tutor — RAG & PDF grounding

The civic AI tutor grounds answers in **published platform content**, not just the model’s training data. Learners see **source citations** in the UI for transparency.

## How retrieval works

1. The learner’s question is tokenized (English + Arabic fragments).
2. **Category intent** is inferred (Constitution, Governance, Elections, Peacebuilding) from keyword sets.
3. For each **published** article, searchable text is built from:
   - **`tutor_index_text`** when present (pre-combined body + PDF text on the article row)
   - Otherwise article body + live PDF extraction via `get_attachment_text()`
4. Text is chunked (~1400 chars, 200 overlap) and scored by keyword overlap with the query.
5. **Controlled documents** and category-matched articles receive a score boost.
6. Top chunks are injected into the Claude system prompt; the API returns a **`sources`** array for the UI.

Implementation:

| Module | Role |
|--------|------|
| `apps/tutor/retrieval.py` | Chunking, scoring, category boost |
| `apps/tutor/document_text.py` | PDF fetch, `pypdf` extraction, Redis cache |
| `apps/learning/tutor_index.py` | Build `Article.tutor_index_text` |
| `apps/learning/signals.py` | Re-index on save; invalidate PDF cache on attachment change |
| `apps/tutor/services.py` | Claude calls, session/history, quotas |

## Dependencies

- **`anthropic`** — Claude API (required for production replies)
- **`pypdf`** — PDF text extraction for attachments

Set `ANTHROPIC_API_KEY` in production. Without it, the tutor returns a development placeholder message.

## API endpoints

All tutor routes require authentication and org membership (`X-Organization-Slug` header for multi-tenant context).

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/tutor/chat/` | Send a message; JSON response with `reply` and `sources[]` |
| POST | `/api/tutor/chat/stream/` | **SSE stream** — events: `token`, `done`, `error` |
| GET | `/api/tutor/chat/session/` | Restore active Redis session (~1 h TTL) |
| DELETE | `/api/tutor/chat/session/` | Clear active session |
| GET | `/api/tutor/chat/history/` | List persisted conversation summaries |
| GET | `/api/tutor/chat/history/<session_id>/` | Load a saved conversation |
| GET | `/api/tutor/usage/` | Daily message budget for the current user |
| GET | `/api/tutor/usage/platform/` | **Platform admin** aggregate usage (today) |

### POST `/api/tutor/chat/` — request

```json
{
  "message": "What rights does the Transitional Constitution guarantee?",
  "article_id": "optional-uuid-for-article-context"
}
```

### POST `/api/tutor/chat/` — response

```json
{
  "session_id": "abc123",
  "reply": "...",
  "sources": [
    {
      "article_id": "uuid",
      "title": "Understanding the Transitional Constitution",
      "source": "Transitional Constitution of the Republic of South Sudan, 2011",
      "category": "Constitution",
      "category_slug": "constitution",
      "source_kind": "text+pdf",
      "excerpt": "…matched chunk…"
    }
  ],
  "tokens_used": 842,
  "messages_used_today": 3,
  "daily_limit": 50,
  "messages_remaining": 47
}
```

### POST `/api/tutor/chat/stream/` — SSE

`Content-Type: text/event-stream`

Events (one per line block):

```
event: token
data: {"text": "The "}

event: done
data: {"session_id": "...", "reply": "...", "sources": [...], "tokens_used": 842, ...}

event: error
data: {"detail": "Daily message limit reached."}
```

The frontend uses this endpoint by default (`frontend/src/lib/tutorStream.js`) with a JSON fallback to `/chat/`.

### GET `/api/tutor/usage/platform/` — platform admin

**Permission:** platform `admin` role only.

```json
{
  "messages_today": 128,
  "tokens_today": 95420,
  "active_users_today": 34
}
```

Use for ops dashboards and cost monitoring alongside `GET /api/integrations/status/`.

## Constitution & PDF content

See **[constitution-content.md](constitution-content.md)** for:

- Seeding via `seed_data` and `seed_assets/`
- Uploading PDFs through the article editor or `POST /api/articles/attachments/upload/`
- Controlled document flags and tutor re-indexing

## Limits & caching

| Mechanism | Detail |
|-----------|--------|
| PDF text cache | Redis, 24 h TTL (`tutor:pdf-text:<hash>`) |
| Cache invalidation | Automatic when `attachment_url` changes (article save signal) |
| `tutor_index_text` | Rebuilt on every article save |
| Retrieval model | Keyword scan per message — no vector DB |
| Daily limits | Plan-gated via `TutorDailyUsage` + billing `tutor_daily_messages` feature |
| Rate limit | `TutorRateThrottle` on chat endpoints |

For large corpora, consider pre-indexing or a vector store in a future release.

## Frontend

| Route | Features |
|-------|----------|
| `/tutor` | Streaming chat, source citations, session restore, history |
| `/articles/:id` | “Ask the AI tutor about this article” → `/tutor?article=<id>` |

## Related docs

- [constitution-content.md](constitution-content.md)
- [api.md](api.md)
- [production-env-checklist.md](production-env-checklist.md) — Anthropic + storage vars
