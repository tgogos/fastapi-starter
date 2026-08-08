# Engineering notes

Decisions for this starter. Prefer simple, robust, boring.

This file is the source of truth for architecture and conventions. When a decision or the code changes, update this document in the same change so it stays accurate for future readers (and agents). Do not refer to chat threads, option letters, or temporary debate labels.

## Goals

- Mature shape (clear modules, auth, tests, Docker) without shortcuts that fight growth.
- One primary full-stack path; optional demos stay thin and removable.
- Async-first; raw SQL (no ORM); Pydantic at the HTTP edge only.

## Product shape

| Surface | Role |
|---------|------|
| SQLite + session/CSRF + HTMX UI + protected SQL JSON API | Primary path — fork and grow this |
| `/items` (in-memory) | Minimal teaching CRUD — no auth, no UI |
| `/db-items` (MongoDB) | Optional NoSQL demo — removable |

Do not add auth, HTMX, or shared abstractions to the memory/Mongo demos unless the point is to teach that idea. Keep demos thin on purpose.

The primary domain entity is named **items**. It may be renamed to something more concrete later (for example books); do not rename until that is decided.

## Code style (primary path)

Write primary-path code like the SQL and web layers:

- Thin route handlers: validate → call a helper → map to the response model.
- SQL in small modules (`app/db/…`, `app/auth/users.py`) with parameterized queries.
- Schema in `app/db/schema.sql`.
- Pydantic models are request/response schemas only, not persistence objects.
- Prefer FastAPI dependencies for auth over ad-hoc checks in every handler.

Reference implementations: `app/routes/sql_items.py`, `app/db/items.py`, `app/web/`.

The in-memory and Mongo routes may stay more verbose (logic in the handler, broad try/except). That style is for demos only — do not copy it into the primary path.

## URL layout

Path indicates the client. Do not serve HTML under `/api`, and do not issue API tokens from the HTML `/auth` routes.

| Prefix | Client | Auth | Response |
|--------|--------|------|----------|
| `/api/...` | Machines (curl, Swagger, services) | Bearer (session also allowed where useful) | JSON |
| `/auth/...` | Browsers | Session cookie + CSRF | HTML (forms, redirects) |
| `/ui/...` | Browsers and HTMX | Session + CSRF on mutations | HTML pages and fragments |
| `/items`, `/db-items` | Teaching demos | None | JSON |
| `/`, `/health`, `/docs` | Ops / docs | — | unchanged |

**Browser auth routes:** `GET/POST /auth/login`, `POST /auth/logout` — establish or clear a session. Logout is POST-only with CSRF (no GET logout). No token issuance here.

**API auth routes:** `POST /api/auth/token` (issue), `DELETE /api/auth/token` (revoke current Bearer), `GET /api/auth/me` (introspect).

**HTMX:** pages and partials share the `/ui/...` prefix (same router). Do not add a separate `/htmx` prefix. Use `templates/` for full pages and `templates/partials/` for fragments.

The SQL JSON API is mounted at `/api/sql-items`. Demos remain at `/items` and `/db-items`.

## Authentication

Teaching overview (cookies, CSRF, Bearer): [`auth.md`](auth.md).

One user store; two client mechanisms:

1. **Browsers / HTMX** — signed session cookie. Mutating HTML/HTMX requests require CSRF (`require_user_html`, `verify_csrf`).
2. **Machine clients** — opaque Bearer token from `POST /api/auth/token` (username/password). Store tokens in SQLite so revocation is deleting a row. Do not default to JWT unless this document is updated to say so.
3. **Protected JSON routes** — `require_user` accepts a valid session **or** a valid Bearer token. If the client uses the **session cookie** on a mutating method (`POST`/`PUT`/`PATCH`/`DELETE`), CSRF is required (`X-CSRF-Token` header or form field). **Bearer requests skip CSRF.**
4. **Same-origin JS calling `/api`** — either send the session cookie with `credentials: "include"` **and** `X-CSRF-Token` (from the page meta tag), or use a Bearer token. Prefer Bearer for non-HTML clients; session+CSRF is fine for page scripts.
5. **Swagger `/docs`** — use HTTP Bearer for `/api` routes. Cookie login is for the UI, not the main docs Authorize flow.

In-memory and Mongo demos remain unauthenticated unless that changes deliberately.

Implemented: session + CSRF for the UI and for session-authenticated `/api` writes; `POST/DELETE /api/auth/token` + opaque tokens in `api_tokens`; `require_user` accepts Bearer or session; Swagger shows HTTP Bearer via `HTTPBearer` on API deps.

## Non-negotiables

- **Async-first** on the request path (async handlers, aiosqlite, Motor). Avoid new sync I/O in handlers. Sync `bcrypt` is an accepted exception; do not add more blocking work without noting it here.
- **No ORM** (no SQLAlchemy, SQLModel, Tortoise, etc.). SQL strings + parameters.
- **Removable modules** — Mongo, web UI, and demos must stay deletable via the README checklist pattern; do not entangle them into the primary path.
- **Document new patterns here** in the same change that introduces them.

## Patterns in use (primary path)

- Lifespan for connect / schema / seed / shutdown (not deprecated `@on_event`).
- Process-wide SQLite connection via `app/db/connection.py` (simple single-process setup; not a pool).
- Repository-style helpers return dicts (or simple structures); routes map to Pydantic.
- Separate dependencies for JSON vs HTML auth: `require_user` (Bearer or session) vs `require_user_html` + `LoginRequired` (session only).
- Opaque API tokens hashed (SHA-256) in `api_tokens`; plaintext returned once from `POST /api/auth/token`.
- Settings via Pydantic Settings (`app/core/config.py`).
- Shared identity helpers in `app/auth/` (passwords, users, tokens, deps). HTTP routes live in `app/routes/` (JSON) and `app/web/` (HTML).
- **uv** for Python deps: `pyproject.toml` + committed `uv.lock`; Docker installs with `uv sync --frozen`. Do not reintroduce `requirements.txt` as a second source of truth. Target CPython **3.14** (`.python-version`, `requires-python`).

## Out of scope

Unless this document is updated first:

- ORMs and sync DB drivers for the primary path
- SPA frameworks or a frontend build step (vanilla JS + HTMX + Pico)
- OAuth2 / OIDC providers
- JWT as the default API token
- A shared abstraction that unifies memory, Mongo, and SQL backends
