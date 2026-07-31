"""HTML auth routes: login / logout."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth.deps import (
    SESSION_USER_KEY,
    get_current_user,
    get_or_create_csrf_token,
)
from app.auth.passwords import verify_password
from app.auth.users import get_user_by_username
from app.web.paths import TEMPLATES_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse(url="/ui/items", status_code=303)
    csrf_token = get_or_create_csrf_token(request)
    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "user": None,
            "csrf_token": csrf_token,
            "error": None,
        },
    )


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
):
    expected = request.session.get("csrf_token")
    if not expected or csrf_token != expected:
        return templates.TemplateResponse(
            request,
            "login.html",
            {
                "user": None,
                "csrf_token": get_or_create_csrf_token(request),
                "error": "Invalid CSRF token. Please try again.",
            },
            status_code=403,
        )

    db_user = await get_user_by_username(username.strip())
    if db_user is None or not verify_password(password, db_user["password_hash"]):
        return templates.TemplateResponse(
            request,
            "login.html",
            {
                "user": None,
                "csrf_token": get_or_create_csrf_token(request),
                "error": "Invalid username or password.",
            },
            status_code=400,
        )

    request.session[SESSION_USER_KEY] = db_user["id"]
    get_or_create_csrf_token(request)
    return RedirectResponse(url="/ui/items", status_code=303)


@router.post("/logout")
async def logout(request: Request, csrf_token: str = Form(None)):
    expected = request.session.get("csrf_token")
    header_token = request.headers.get("X-CSRF-Token")
    provided = header_token or csrf_token
    if expected and provided == expected:
        request.session.clear()
    elif expected is None:
        request.session.clear()
    else:
        # Still clear session on logout attempt with bad CSRF to avoid lock-in,
        # but prefer validating when possible.
        request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=303)


@router.get("/logout")
async def logout_get(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=303)
