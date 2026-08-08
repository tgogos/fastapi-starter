# Standard library imports
from contextlib import asynccontextmanager

# Third-party imports
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

# Local imports
from app.auth.exceptions import LoginRequired
from app.core import config
from app.routes import root, items, db_items, sql_items, api_auth
from app.web import auth_routes, items_routes
from app.web.paths import STATIC_DIR

description = """
### Root
- Root endpoint of the API. Just a welcome message.
- Health-check endpoint.

### Items (demo)
- CRUD operations for items (in-memory storage).

### Database Items (demo)
- CRUD operations for items (MongoDB storage).

### API auth
- `POST /api/auth/token` — username/password → opaque Bearer token.
- `GET /api/auth/me` — current user (Bearer or session).

### SQL Items (primary)
- CRUD under `/api/sql-items` (SQLite).
- Writes require Bearer token or session cookie.

### Web UI
- Pico CSS + HTMX under `/ui`; browser login under `/auth`.
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.utils.mongo import connect_to_mongo, close_mongo_connection
    from app.db.connection import connect_to_sqlite, close_sqlite
    from app.auth.seed import seed_demo_user

    await connect_to_mongo()
    await connect_to_sqlite()
    await seed_demo_user()
    yield
    await close_sqlite()
    await close_mongo_connection()


app = FastAPI(
    title="FastAPI starter",
    description=description,
    summary="FastAPI starter documentation",
    version=config.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=config.SECRET_KEY,
    session_cookie=config.SESSION_COOKIE_NAME,
    same_site="lax",
    https_only=False,
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.exception_handler(LoginRequired)
async def login_required_handler(request: Request, exc: LoginRequired):
    return RedirectResponse(url="/auth/login", status_code=303)


# JSON API (demos stay at top level; primary path under /api)
app.include_router(root.router, prefix="", tags=["root"])
app.include_router(items.router, prefix="/items", tags=["items"])
app.include_router(db_items.router, prefix="/db-items", tags=["database-items"])
app.include_router(api_auth.router, prefix="/api/auth", tags=["auth-api"])
app.include_router(sql_items.router, prefix="/api/sql-items", tags=["sql-items"])

# HTML / HTMX (removable with app/web/)
app.include_router(auth_routes.router, prefix="/auth", tags=["auth-web"])
app.include_router(items_routes.router, prefix="/ui", tags=["ui"])
