# FastAPI Starter

A minimal FastAPI starter template with JSON APIs, MongoDB, SQLite, session auth, and an optional Pico/HTMX UI.

## Features

- **RESTful API**
  - In-memory storage (`/items`) — demo
  - MongoDB persistent storage (`/db-items`) — demo
  - SQLite persistent storage (`/api/sql-items`) — writes require Bearer token or session
- **Web UI** (removable): Pico CSS + HTMX + vanilla JS under `/ui` and `/auth`
- **Auth**:
  - Browser: signed cookie sessions + CSRF on mutating HTML/HTMX requests
  - API: `POST /api/auth/token` → opaque Bearer token (Swagger Authorize)
- **Configuration**: Pydantic Settings with environment variable validation
- **Testing**: pytest suite (in-memory items, SQL items, token + session auth)
- **Docker Compose** with hot reload

## Project Structure

```
fastapi-starter/
├── app/
│   ├── core/           # Configuration (Pydantic Settings)
│   ├── models/         # Pydantic schemas
│   ├── routes/         # JSON API routers
│   ├── db/             # SQLite connection + schema (removable)
│   ├── auth/           # Passwords, session deps, demo user seed
│   ├── utils/          # Mongo helpers
│   ├── web/            # HTML/HTMX templates + static (removable)
│   └── main.py
├── tests/
├── docs/               # Engineering decisions
├── data/               # SQLite file (gitignored *.db)
├── AGENTS.md
├── docker-compose.yml
├── docker-compose.dev.yml
├── Dockerfile
├── Makefile
└── requirements.txt
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Make (optional)

### Development

```bash
make dotenv   # copies .env.example → .env
make upd      # build + start (detached)

# API:        http://localhost:8000
# Docs:       http://localhost:8000/docs  (Authorize with Bearer from /api/auth/token)
# Web UI:     http://localhost:8000/ui/items  (login first)
# Login:      http://localhost:8000/auth/login
```

### API token (Swagger / curl)

```bash
curl -s -X POST http://localhost:8000/api/auth/token \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}'
# → {"access_token":"...","token_type":"bearer"}

curl -s http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

In `/docs`, call **POST /api/auth/token**, then **Authorize** and paste the `access_token` as a Bearer token.

### Demo login

When the `users` table is empty, a demo user is seeded:

| Variable | Default |
|----------|---------|
| `DEMO_USERNAME` | `admin` |
| `DEMO_PASSWORD` | `admin123` |

Change these (and especially `SECRET_KEY`) before any shared deployment.

### Make targets

| Command | Description |
|---------|-------------|
| `make dotenv` | Create `.env` from `.env.example` |
| `make build` | Build images |
| `make up` / `make upd` | Start (foreground / detached) |
| `make down` / `make downv` | Stop / stop + volumes |
| `make test` | Run pytest in the app container |

## Configuration

Priority: OS environment → `.env` → defaults.

| Variable | Default | Description |
|----------|---------|-------------|
| `VERSION` | `0.1.0` | App version |
| `ENVIRONMENT` | `development` | Runtime environment |
| `DEBUG` | `false` | When `true`, prints config sources on startup |
| `PUBLISH_PORT` | `8000` | Host port |
| `SECRET_KEY` | `change-me-in-production` | Session signing key |
| `SESSION_COOKIE_NAME` | `fastapi_starter_session` | Cookie name |
| `DEMO_USERNAME` / `DEMO_PASSWORD` | `admin` / `admin123` | Seeded if no users exist |
| `DATABASE_URL` | `sqlite:///./data/app.db` | SQLite path URL |
| `MONGO_*` | (see `.env.example`) | MongoDB connection |

## Removing modules (fork checklist)

### API-only (drop HTMX UI)

1. Delete `app/web/`
2. In `app/main.py`, remove `StaticFiles` mount, `LoginRequired` handler, and `auth_routes` / `items_routes` includes
3. Optionally drop session middleware if you do not need cookie auth for JSON

### NoSQL-only (drop SQLite + SQL UI)

1. Delete `app/db/`, `app/auth/` (if unused), `app/routes/sql_items.py`, `app/routes/api_auth.py`, `app/models/sql_item.py`, `app/models/auth.py`
2. Remove SQLite connect/seed from lifespan; remove `/api/sql-items` and `/api/auth` routers
3. Remove or slim `app/web/` if it only demos SQL items
4. Drop `aiosqlite` / `bcrypt` from `requirements.txt` if unused
5. Remove `data/` volume mounts from Compose

### No Mongo

1. Delete `app/utils/mongo.py` usage, `app/routes/db_items.py`, `app/models/db_item.py`
2. Remove Mongo from lifespan and Compose `mongodb` service

## Application bootstrap

Lifespan (not deprecated `@on_event`):

1. Connect MongoDB
2. Connect SQLite, apply `app/db/schema.sql`
3. Seed demo user if `users` is empty
4. On shutdown: close SQLite, then Mongo

## Testing

```bash
make upd
make test
# or: docker compose -f docker-compose.dev.yml exec fastapi-starter pytest -v
```

Coverage includes in-memory `/items`, `/api/sql-items` CRUD (session and Bearer), `/api/auth/token`, login page, and `/ui/items` redirect when anonymous.

## License

MIT — see [LICENSE](LICENSE).
