# Testing & CI

How CivicHub is verified in CI and locally.

## CI pipeline (`.github/workflows/ci.yml`)

| Job | What it runs |
|-----|----------------|
| **security** | Bandit SAST, Safety dependency scan, Gitleaks |
| **backend** | `makemigrations --check`, pytest with **≥80% coverage**, deploy checks |
| **frontend** | ESLint, Vitest, Vite build, **mocked Playwright e2e** |
| **e2e-live** | Postgres + `seed_data`, real Django + Vite, **live Playwright e2e** |
| **loadtest** | `smoke_check`, `check_integrations --json`, Locust gate |
| **disaster-recovery** | `restore_database_drill` |

The **e2e-live** job runs only after **backend** passes (`needs: [backend]`).

## Backend tests

```bash
cd backend
pytest -q
pytest -q --cov=apps --cov-fail-under=80
```

Key tutor coverage:

| File | Covers |
|------|--------|
| `tests/test_tutor.py` | Chat, limits, session, usage, **platform admin usage** |
| `tests/test_tutor_retrieval.py` | RAG chunking, PDF text, category routing |
| `tests/test_medium_features.py` | Tutor history & session restore |
| `tests/test_low_vision_features.py` | SSE stream endpoint, `tutor_index_text` |

## Frontend unit tests (Vitest)

```bash
cd frontend
npm run test
npm run test:watch
```

App source is **JavaScript (`.jsx`)** — Vitest and Testing Library cover pages and libs. A full TypeScript migration is optional future work; CI does not require `.tsx` in `src/`.

## E2E tests (Playwright)

Two modes via `E2E_LIVE`:

### Mocked API (default — `frontend` CI job)

Uses route interception; no backend required. Specs: `frontend/e2e/*.spec.js`.

```bash
cd frontend
npx playwright install chromium
npm run test:e2e
```

Includes **tutor** flow (`e2e/tutor.spec.js`): SSE stream mock, reply + source citations.

### Live backend (`e2e-live` CI job)

Starts real Django (`seed_data`) + Vite dev server. Specs: `frontend/e2e/live/**/*.spec.js`.

```bash
# Terminal 1 — backend
cd backend
python manage.py migrate && python manage.py seed_data
python manage.py runserver

# Terminal 2 — frontend live e2e
cd frontend
$env:E2E_LIVE="1"   # PowerShell
npm run test:e2e:live
```

Live specs include:

| Spec | Coverage |
|------|----------|
| `live/login.spec.js` | Real login, `/api/ready/` |
| `live/articles.spec.js` | Seeded articles list |
| `live/quiz.spec.js` | Quiz list from API |
| `live/forum.spec.js` | Seeded forum topic |
| `live/tutor.spec.js` | **Tutor chat API, SSE stream, admin usage, UI chat** |

Shared helpers: `frontend/e2e/helpers.js` (`loginLive`, `seedLiveAuth`, `mockSession`).

### Environment variables (live e2e)

| Variable | Default |
|----------|---------|
| `E2E_LIVE` | `1` enables live mode |
| `E2E_API_URL` | `http://127.0.0.1:8000` |
| `E2E_WEB_URL` | `http://127.0.0.1:5173` |
| `E2E_ADMIN_EMAIL` | `admin@civic-education.ss` |
| `E2E_ADMIN_PASSWORD` | `AdminPass123!` |
| `E2E_ORG_SLUG` | `platform-demo` |

With no AI provider configured, the tutor returns a **development stub** — live tutor tests accept stub or real replies.

## Ops smoke (loadtest job)

```bash
cd backend
python manage.py smoke_check --base-url http://127.0.0.1:8000
python manage.py check_integrations --json
python manage.py check_integrations --strict
```

## Related docs

- [api.md](api.md) — endpoint index
- [tutor-rag.md](tutor-rag.md) — tutor API detail
- [production-launch.md](production-launch.md) — pre-deploy checklist
