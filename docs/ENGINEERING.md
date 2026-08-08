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
| SQLite + session/CSRF + HTMX UI + protected books JSON API | Primary path — fork and grow this |
| `/items` (in-memory) | Minimal teaching CRUD — no auth, no UI |
| `/db-items` (MongoDB) | Optional NoSQL demo — removable |

Do not add auth, HTMX, or shared abstractions to the memory/Mongo demos unless the point is to teach that idea. Keep demos thin on purpose.

The primary domain entity is **books**. Demo routes keep the thin **Item** CRUD naming (`/items`, `/db-items`) on purpose — they teach storage, not a second books product.

## Roles

Three hierarchical roles on `users.role`:

| Role | Capabilities |
|------|----------------|
| `viewer` | Read books (UI + API GET) |
| `editor` | Create / update / delete books |
| `admin` | Editor powers + `/ui/admin/users` (list users, change roles) |

Enforcement is always on the server (`require_user` / `require_editor` / `require_admin` and HTML variants). Templates hide buttons; never trust the UI alone.

The seeded demo user is an **admin** (`DEMO_USERNAME` / `DEMO_PASSWORD`).

Startup only ensures that admin when `users` is empty. Richer demo data (sample `viewer` / `editor` accounts and books) is opt-in via `python -m app.seed` / `make seed` — idempotent (skips existing usernames; inserts only missing sample book titles). Sample list is larger than the UI page size (10) so pagination is easy to exercise.

## Code style (primary path)

Write primary-path code like the SQL and web layers:

- Thin route handlers: validate → call a helper → map to the response model.
- SQL in small modules (`app/db/…`, `app/auth/users.py`) with parameterized queries.
- Schema in `app/db/schema.sql`.
- Pydantic models are request/response schemas only, not persistence objects.
- Prefer FastAPI dependencies for auth over ad-hoc checks in every handler.

Reference implementations: `app/routes/books.py`, `app/db/books.py`, `app/web/books_routes.py`.

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

**API auth routes:** `POST /api/auth/token` (issue), `DELETE /api/auth/token` (revoke current Bearer), `GET /api/auth/me` (introspect, includes `role`).

**HTMX:** pages and partials share the `/ui/...` prefix (same router). Do not add a separate `/htmx` prefix. Use `templates/` for full pages and `templates/partials/` for fragments.

Primary mounts:

| Surface | Path |
|---------|------|
| UI list / HTMX | `/ui/books` (full page or partial via `HX-Request`) |
| Staff | `/ui/admin/users` (admin only) |
| JSON API | `/api/books` (reads: login; writes: editor+) |
| Root | `/` → `/ui/books` |

Demos remain at `/items` and `/db-items`.

### HTMX patterns in use

- **`HX-Request` dual response** — one list route returns the full page or `partials/books_table.html`.
- **Search** — `q` on title/author with debounce + `hx-push-url`.
- **Pagination** — `page` / `size` query params, same dual-response + push URL.
- **Indicator** — `hx-indicator` on search/list swaps.
- Progressive enhancement: pagination links keep usable `href`s.

Out of scope for now (do not add without updating this doc): Alpine.js, HTMX out-of-band (`hx-swap-oob`) swaps, i18n.

## Authentication

Teaching overview (cookies, CSRF, Bearer): [`auth.md`](auth.md).

One user store; two client mechanisms:

1. **Browsers / HTMX** — signed session cookie. Mutating HTML/HTMX requests require CSRF (`require_user_html`, `verify_csrf`).
2. **Machine clients** — opaque Bearer token from `POST /api/auth/token` (username/password). Store tokens in SQLite so revocation is deleting a row. Do not default to JWT unless this document is updated to say so.
3. **Protected JSON routes** — `require_user` accepts a valid session **or** a valid Bearer token. If the client uses the **session cookie** on a mutating method (`POST`/`PUT`/`PATCH`/`DELETE`), CSRF is required (`X-CSRF-Token` header or form field). **Bearer requests skip CSRF.** Role gates: `require_editor`, `require_admin`.
4. **Same-origin JS calling `/api`** — either send the session cookie with `credentials: "include"` **and** `X-CSRF-Token` (from the page meta tag), or use a Bearer token. Prefer Bearer for non-HTML clients; session+CSRF is fine for page scripts.
5. **Swagger `/docs`** — use HTTP Bearer for `/api` routes. Cookie login is for the UI, not the main docs Authorize flow.

In-memory and Mongo demos remain unauthenticated unless that changes deliberately.

Implemented: session + CSRF for the UI and for session-authenticated `/api` writes; `POST/DELETE /api/auth/token` + opaque tokens in `api_tokens`; `require_user` accepts Bearer or session; Swagger shows HTTP Bearer via `HTTPBearer` on API deps.

## Schema / local SQLite

`CREATE TABLE IF NOT EXISTS` does not migrate existing databases. After schema changes (e.g. `users.role`, `books` replacing `sql_items`), delete local `data/*.db` (and test DBs) and restart so tables are recreated. The starter prefers recreate over Alembic.

## Non-negotiables

- **Async-first** on the request path (async handlers, aiosqlite, Motor). Avoid new sync I/O in handlers. Sync `bcrypt` is an accepted exception; do not add more blocking work without noting it here.
- **No ORM** (no SQLAlchemy, SQLModel, Tortoise, etc.). SQL strings + parameters.
- **Removable modules** — Mongo, web UI, and demos must stay deletable via the README checklist pattern; do not entangle them into the primary path.
- **Document new patterns here** in the same change that introduces them.

## Patterns in use (primary path)

- Lifespan for connect / schema / seed / shutdown (not deprecated `@on_event`).
- Process-wide SQLite connection via `app/db/connection.py` (simple single-process setup; not a pool).
- Repository-style helpers return dicts (or simple structures); routes map to Pydantic.
- Separate dependencies for JSON vs HTML auth: `require_user` (Bearer or session) vs `require_user_html` + `LoginRequired` (session only); plus `require_editor` / `require_admin` (and HTML variants).
- Opaque API tokens hashed (SHA-256) in `api_tokens`; plaintext returned once from `POST /api/auth/token`.
- Settings via Pydantic Settings (`app/core/config.py`).
- Shared identity helpers in `app/auth/` (passwords, users, tokens, deps). HTTP routes live in `app/routes/` (JSON) and `app/web/` (HTML).
- **uv** for Python deps: `pyproject.toml` + committed `uv.lock`; Docker installs with `uv sync --frozen`. Do not reintroduce `requirements.txt` as a second source of truth. Target CPython **3.14** (`.python-version`, `requires-python`).

## Out of scope

Unless this document is updated first:

- ORMs and sync DB drivers for the primary path
- SPA frameworks or a frontend build step (vanilla JS + HTMX + Pico)
- Alpine.js, HTMX OOB swaps, i18n
- OAuth2 / OIDC providers
- JWT as the default API token
- Django-style generic admin
