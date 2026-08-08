# Agent notes

Before changing this repo, read [`docs/ENGINEERING.md`](docs/ENGINEERING.md) and follow it.

## Must follow

- Prefer the primary path: SQLite, session/CSRF + HTMX UI, protected SQL JSON API. Keep in-memory and Mongo demos thin and removable.
- Async-first on the request path. No ORM — parameterized SQL only. Pydantic for request/response schemas, not persistence.
- Match primary-path style: thin routes, SQL/helpers in `app/db/` (and `app/auth/` for users), HTML/HTMX under `app/web/`.
- URL intent: `/api` = JSON (machines), `/auth` = HTML session, `/ui` = pages + HTMX fragments. Do not invent a separate `/htmx` prefix.
- Auth direction: browser session + CSRF; API Bearer opaque tokens in SQLite; protected JSON accepts session or Bearer. Session-authenticated mutating `/api` calls require CSRF. Do not default to JWT or OAuth unless `ENGINEERING.md` says so.
- Do not rename the `items` domain until that is decided in `ENGINEERING.md`.
- Do not introduce new architectural patterns without updating `docs/ENGINEERING.md` in the same change.
- Python deps: **uv** only (`pyproject.toml` + `uv.lock`). Do not add `requirements.txt`.

## Scope

Only change what the task requires. Do not “improve” demo routes (`/items`, `/db-items`) toward the primary stack unless asked.
