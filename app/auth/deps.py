"""FastAPI dependencies for session auth and CSRF."""

from __future__ import annotations

import secrets
from typing import Any, Optional

from fastapi import Depends, HTTPException, Request, status

from app.auth.exceptions import LoginRequired
from app.auth.users import get_user_by_id

SESSION_USER_KEY = "user_id"
SESSION_CSRF_KEY = "csrf_token"


def get_or_create_csrf_token(request: Request) -> str:
    token = request.session.get(SESSION_CSRF_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        request.session[SESSION_CSRF_KEY] = token
    return token


async def verify_csrf(request: Request) -> None:
    """Validate CSRF from X-CSRF-Token header or csrf_token form field."""
    expected = request.session.get(SESSION_CSRF_KEY)
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing from session",
        )

    provided = request.headers.get("X-CSRF-Token")
    if not provided and request.method in ("POST", "PUT", "PATCH", "DELETE"):
        content_type = request.headers.get("content-type", "")
        if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
            form = await request.form()
            provided = form.get("csrf_token")

    if provided != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token",
        )


# Backwards-friendly alias used in __init__
ensure_csrf = verify_csrf


async def get_current_user(request: Request) -> Optional[dict[str, Any]]:
    user_id = request.session.get(SESSION_USER_KEY)
    if user_id is None:
        return None
    user = await get_user_by_id(int(user_id))
    if user is None:
        request.session.pop(SESSION_USER_KEY, None)
        return None
    return {"id": user["id"], "username": user["username"]}


async def require_user(
    user: Optional[dict[str, Any]] = Depends(get_current_user),
) -> dict[str, Any]:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user


async def require_user_html(request: Request) -> dict[str, Any]:
    """Require login for HTML routes; redirects via LoginRequired handler."""
    user = await get_current_user(request)
    if user is None:
        raise LoginRequired()
    return user