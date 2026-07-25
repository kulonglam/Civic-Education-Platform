# Constitution & controlled documents

How to publish the Transitional Constitution (or other long PDFs) so the **AI tutor** can ground answers in official text.

## Overview

The tutor retrieves chunks from:

1. **Article body** (Markdown)
2. **PDF attachments** on published articles (extracted with `pypdf`)
3. **`tutor_index_text`** — a pre-built index on each article (body + PDF text), refreshed on save

Controlled documents get a retrieval boost so constitutional questions prefer official sources.

---

## Option A — Seed data (recommended for demos)

### 1. Add source files

Place files under:

```
backend/apps/accounts/management/commands/seed_assets/
├── transitional-constitution.txt      # full plain text (preferred for RAG)
├── transitional-constitution.pdf    # official PDF (optional but recommended)
└ transitional-constitution-sample.pdf  # fallback sample PDF (already in repo)
```

| File | Purpose |
|------|---------|
| `transitional-constitution.txt` | Injected into the article body; best tutor coverage |
| `transitional-constitution.pdf` | Official PDF attachment; used when present |
| `transitional-constitution-sample.pdf` | Used only if the official PDF is missing |

### 2. Run seed

```bash
cd backend
python manage.py seed_data
```

This creates or updates **Understanding the Transitional Constitution** under the **Constitution** category with:

- Full text from `.txt` when available
- PDF attachment uploaded to Supabase/local storage
- `is_controlled_document=True` and a `document_label` for citations

Re-run `seed_data` after replacing the official PDF — the command upgrades existing articles and re-attaches files.

### 3. Verify

- Open the article on the frontend (`/articles/<id>`)
- Open **AI Tutor** from the article (“Ask the AI tutor about this article”)
- Ask a constitutional question — the response should include **Sources** linking back to the article

---

## Option B — Article editor (production / org admins)

Content managers and platform editors can publish controlled documents without re-running seed.

### UI path

1. Log in as org **content manager** or platform **editor/admin**
2. Go to **Manage articles** → **New article** (`/articles/new`) or edit an existing draft
3. Fill title, category (**Constitution**), and Markdown body (summary or full text)
4. Under **PDF attachment**, upload a `.pdf` (max 20 MB for tutor extraction)
5. Check **Controlled document** and set:
   - **Document label** — e.g. `Transitional Constitution of the Republic of South Sudan, 2011`
   - **Attachment version** — e.g. `2011-07-09`
6. Set status to **Published** and save

### API path

```http
POST /api/articles/attachments/upload/
Authorization: Bearer <token>
X-Organization-Slug: your-org-slug
Content-Type: multipart/form-data

file=<pdf-bytes>
```

Response includes `attachment_url` and `attachment_name`. Include those fields when creating/updating the article:

```http
POST /api/articles/
PATCH /api/articles/<id>/
```

```json
{
  "title": "Transitional Constitution",
  "category": "<category-uuid>",
  "content": "## Overview\n\n...",
  "status": "published",
  "attachment_url": "https://.../articles/.../constitution.pdf",
  "attachment_name": "Transitional Constitution.pdf",
  "is_controlled_document": true,
  "document_label": "Transitional Constitution of the Republic of South Sudan, 2011",
  "attachment_version": "2011-07-09"
}
```

### What happens on save

Django signals (`apps/learning/signals.py`):

1. Rebuild `tutor_index_text` from body + extracted PDF text
2. Invalidate the Redis PDF text cache for the old attachment URL (if replaced)

No manual re-index step is required.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Tutor ignores constitution | Confirm article **status=published** and category slug is `constitution` |
| Sample PDF warning after seed | Add `transitional-constitution.pdf` to `seed_assets/` and re-run `seed_data` |
| Stale answers after PDF swap | Save the article again (triggers cache invalidation + index rebuild) |
| Empty PDF text | Ensure file is a text-based PDF (scanned images need OCR — not supported) |
| Attachment too large | Tutor skips PDFs over 20 MB (`document_text.py`) |

---

## Related docs

- [tutor-rag.md](tutor-rag.md) — retrieval algorithm, endpoints, streaming
- [api.md](api.md) — full API index
- [production-env-checklist.md](production-env-checklist.md) — `ANTHROPIC_API_KEY`, Supabase storage
