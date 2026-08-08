# FastAPI Starter

Boilerplate for a **server-driven web UI with FastAPI + HTMX** (no SPA, no Node build) that also exposes a **JSON REST API** for other clients (mobile apps, scripts, etc.).

Browsers get HTML (Jinja + [Pico CSS](https://picocss.com/) + [HTMX](https://htmx.org/)). Machines get `/api` with Bearer tokens. One user store, Docker Compose, pytest.

Architecture and conventions: [`docs/ENGINEERING.md`](docs/ENGINEERING.md).

## Primary path vs demos

| | Role |
|--|------|
| **Primary** | SQLite · session + CSRF for `/ui` and `/auth` · Bearer (or session) for `/api/sql-items` · Pico/HTMX UI |
| **Demos** (thin, removable) | `/items` in-memory CRUD · `/db-items` MongoDB CRUD — teaching surfaces, not the main app |

Fork and grow the primary path. Keep demos minimal or delete them.

## Quick start

**Requires:** Docker Compose. Make is optional.

```bash
make dotenv   # .env.example → .env
make upd      # build + start (detached)

# http://localhost:8000           → redirects to /ui/items
# http://localhost:8000/ui/items  → UI (login first)
# http://localhost:8000/auth/login
# http://localhost:8000/docs      → OpenAPI (JSON API only)
```

Demo user (seeded when `users` is empty): `DEMO_USERNAME` / `DEMO_PASSWORD` (defaults `admin` / `admin123`). Change these and **`SECRET_KEY`** before any shared deploy.

```bash
make test     # pytest in the app container
make down     # stop
```

## Auth in brief

- **Browser / HTMX:** cookie session + CSRF on mutating HTML (`/auth`, `/ui`).
- **API:** Bearer via `POST /api/auth/token`, or session cookie. Session writes to `/api` need `X-CSRF-Token` (same token as `<meta name="csrf-token">` on UI pages). Bearer skips CSRF.
- **Page JS → `/api`:** `credentials: "include"` + `X-CSRF-Token`, or `Authorization: Bearer …`.

```bash
curl -s -X POST http://localhost:8000/api/auth/token \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}'
```

## Stack notes

- Async-first (aiosqlite, Motor for the Mongo demo).
- SQL without an ORM (`schema.sql` + parameterized queries).
- Pydantic for request/response schemas only.
- No frontend toolchain: templates + static HTMX/Pico/JS.

Details and non-negotiables: [`docs/ENGINEERING.md`](docs/ENGINEERING.md).

## Configuration

Priority: OS environment → `.env` → defaults. See [`.env.example`](.env.example) for the full list.

| Variable | Notes |
|----------|--------|
| `SECRET_KEY` | Session signing — change for any real deploy |
| `DEMO_USERNAME` / `DEMO_PASSWORD` | Seeded only when no users exist |
| `PUBLISH_PORT` | Host port (default `8000`) |
| `DATABASE_URL` | SQLite URL (default `sqlite:///./data/app.db`) |
| `MONGO_*` | Only needed for the Mongo demo |

## Layout

```
app/
  auth/     # passwords, users, tokens, deps
  db/       # SQLite connection + schema (primary)
  routes/   # JSON API (/api/..., demos)
  web/      # HTML/HTMX templates + static (removable)
  models/   # Pydantic schemas
  core/     # settings
docs/       # ENGINEERING.md
```

## Removing pieces

- **No UI:** delete `app/web/`; drop static mount and web routers in `main.py`.
- **No Mongo demo:** drop `db_items` / `mongo` helpers, lifespan connect, Compose `mongodb` service.
- **No memory demo:** drop `app/routes/items.py` and its include.

More checklist detail lives in git history / `ENGINEERING.md` if you need it; the primary app does not depend on the demos.

## License

MIT — see [LICENSE](LICENSE).
