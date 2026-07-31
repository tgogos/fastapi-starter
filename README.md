# FastAPI Starter

A minimal FastAPI starter template with JSON APIs, MongoDB, SQLite, session auth, and an optional Pico/HTMX UI.

## Features

- **RESTful API**
  - In-memory storage (`/items`)
  - MongoDB persistent storage (`/db-items`)
  - SQLite persistent storage (`/sql-items`) — writes require login
- **Web UI** (removable): Pico CSS + HTMX + vanilla JS under `/ui` and `/auth`
- **Auth**: signed cookie sessions, CSRF on mutating HTML/HTMX requests
- **Configuration**: Pydantic Settings with environment variable validation
- **Testing**: pytest suite (in-memory items, SQL items, login redirects)
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
├── data/               # SQLite file (gitignored *.db)
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
# Docs:       http://localhost:8000/docs
# Web UI:     http://localhost:8000/ui/items  (login first)
# Login:      http://localhost:8000/auth/login
```

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

1. Delete `app/db/`, `app/auth/` (if unused), `app/routes/sql_items.py`, `app/models/sql_item.py`
2. Remove SQLite connect/seed from lifespan; remove `/sql-items` router
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

Coverage includes in-memory `/items`, `/sql-items` CRUD (auth-gated writes), login page, and `/ui/items` redirect when anonymous.

## License

MIT — see [LICENSE](LICENSE).
