"""HTML / HTMX routes for books UI and admin users."""

from __future__ import annotations

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.auth.deps import (
    get_or_create_csrf_token,
    require_admin_html,
    require_editor_html,
    require_user_html,
    verify_csrf,
)
from app.auth.users import (
    ROLES,
    count_admins,
    list_users,
    normalize_role,
    role_at_least,
    set_user_role,
)
from app.db import books as books_repo
from app.web.paths import TEMPLATES_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

DEFAULT_PAGE_SIZE = 10


def _can_edit(user: dict) -> bool:
    return role_at_least(user["role"], "editor")


def _ctx(request: Request, user: dict, **extra):
    return {
        "request": request,
        "user": user,
        "csrf_token": get_or_create_csrf_token(request),
        "can_edit": _can_edit(user),
        "is_admin": role_at_least(user["role"], "admin"),
        **extra,
    }


def _books_list_url(page: int, size: int, q: str | None) -> str:
    params: dict[str, str | int] = {"page": page, "size": size}
    if q:
        params["q"] = q
    return f"/ui/books?{urlencode(params)}"


async def _books_page_data(
    page: int,
    size: int,
    q: str | None,
) -> dict:
    rows, total = await books_repo.list_books(page=page, size=size, q=q)
    pages = books_repo.total_pages(total, size)
    return {
        "books": rows,
        "total": total,
        "page": page,
        "size": size,
        "total_pages": pages,
        "q": q or "",
        "prev_url": _books_list_url(page - 1, size, q) if page > 1 else None,
        "next_url": (
            _books_list_url(page + 1, size, q) if pages and page < pages else None
        ),
    }


@router.get("/books", response_class=HTMLResponse)
async def books_page(
    request: Request,
    user: dict = Depends(require_user_html),
    page: int = Query(1, ge=1),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=100),
    q: str | None = Query(None),
):
    data = await _books_page_data(page, size, q)
    template = (
        "partials/books_table.html"
        if request.headers.get("HX-Request") == "true"
        else "books.html"
    )
    return templates.TemplateResponse(request, template, _ctx(request, user, **data))


@router.post(
    "/books",
    response_class=HTMLResponse,
    dependencies=[Depends(verify_csrf)],
)
async def create_book(
    request: Request,
    user: dict = Depends(require_editor_html),
    title: str = Form(...),
    author: str = Form(...),
    year: str = Form(""),
    notes: str = Form(""),
    page: int = Query(1, ge=1),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=100),
    q: str | None = Query(None),
):
    title = title.strip()
    author = author.strip()
    notes_val = notes.strip() or None
    year_val: int | None = None
    form_error = None

    if not title or not author:
        form_error = "Title and author are required."
    elif year.strip():
        try:
            year_val = int(year.strip())
            if year_val < 0 or year_val > 9999:
                form_error = "Year must be between 0 and 9999."
        except ValueError:
            form_error = "Year must be a number."

    if form_error is None:
        await books_repo.create_book(title, author, year=year_val, notes=notes_val)
        page = 1

    data = await _books_page_data(page, size, q)
    return templates.TemplateResponse(
        request,
        "partials/books_table.html",
        _ctx(request, user, form_error=form_error, **data),
        status_code=400 if form_error else 200,
    )


@router.get("/books/{book_id}/edit", response_class=HTMLResponse)
async def edit_book_form(
    request: Request,
    book_id: str,
    user: dict = Depends(require_editor_html),
):
    book = await books_repo.get_book(book_id)
    if book is None:
        return HTMLResponse("Book not found", status_code=404)
    return templates.TemplateResponse(
        request,
        "partials/book_edit_row.html",
        _ctx(
            request,
            user,
            book=book,
            page=1,
            size=DEFAULT_PAGE_SIZE,
            q="",
        ),
    )


@router.get("/books/{book_id}/row", response_class=HTMLResponse)
async def book_row(
    request: Request,
    book_id: str,
    user: dict = Depends(require_user_html),
):
    book = await books_repo.get_book(book_id)
    if book is None:
        return HTMLResponse("Book not found", status_code=404)
    return templates.TemplateResponse(
        request,
        "partials/book_row.html",
        _ctx(
            request,
            user,
            book=book,
            page=1,
            size=DEFAULT_PAGE_SIZE,
            q="",
        ),
    )


@router.put(
    "/books/{book_id}",
    response_class=HTMLResponse,
    dependencies=[Depends(verify_csrf)],
)
async def update_book(
    request: Request,
    book_id: str,
    user: dict = Depends(require_editor_html),
    title: str = Form(...),
    author: str = Form(...),
    year: str = Form(""),
    notes: str = Form(""),
):
    title = title.strip()
    author = author.strip()
    notes_val = notes.strip() or None
    year_val: int | None = None
    if year.strip():
        try:
            year_val = int(year.strip())
        except ValueError:
            return HTMLResponse("Invalid year", status_code=400)
    else:
        year_val = None

    book = await books_repo.update_book(
        book_id,
        title=title,
        author=author,
        year=year_val,
        year_set=True,
        notes=notes_val,
        notes_set=True,
    )
    if book is None:
        return HTMLResponse("Book not found", status_code=404)
    return templates.TemplateResponse(
        request,
        "partials/book_row.html",
        _ctx(
            request,
            user,
            book=book,
            page=1,
            size=DEFAULT_PAGE_SIZE,
            q="",
        ),
    )


@router.delete(
    "/books/{book_id}",
    response_class=HTMLResponse,
    dependencies=[Depends(verify_csrf)],
)
async def delete_book(
    request: Request,
    book_id: str,
    user: dict = Depends(require_editor_html),
    page: int = Query(1, ge=1),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=100),
    q: str | None = Query(None),
):
    await books_repo.delete_book(book_id)
    data = await _books_page_data(page, size, q)
    if data["total"] and page > data["total_pages"]:
        page = data["total_pages"]
        data = await _books_page_data(page, size, q)
    return templates.TemplateResponse(
        request,
        "partials/books_table.html",
        _ctx(request, user, **data),
    )


@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(
    request: Request,
    user: dict = Depends(require_admin_html),
):
    users = await list_users()
    return templates.TemplateResponse(
        request,
        "admin_users.html",
        _ctx(
            request,
            user,
            users=users,
            roles=sorted(ROLES),
            form_error=None,
            form_ok=None,
        ),
    )


@router.post(
    "/admin/users/{user_id}/role",
    response_class=HTMLResponse,
    dependencies=[Depends(verify_csrf)],
)
async def admin_set_role(
    request: Request,
    user_id: int,
    user: dict = Depends(require_admin_html),
    role: str = Form(...),
):
    role = normalize_role(role.strip())
    form_error = None
    form_ok = None

    if role not in ROLES:
        form_error = "Invalid role."
    else:
        target = next((u for u in await list_users() if u["id"] == user_id), None)
        if target is None:
            form_error = "User not found."
        elif (
            target["role"] == "admin"
            and role != "admin"
            and await count_admins() <= 1
        ):
            form_error = "Cannot demote the last admin."
        else:
            updated = await set_user_role(user_id, role)
            if updated is None:
                form_error = "User not found."
            else:
                form_ok = f"Updated {updated['username']} to {updated['role']}."

    users = await list_users()
    return templates.TemplateResponse(
        request,
        "partials/admin_users_table.html",
        _ctx(
            request,
            user,
            users=users,
            roles=sorted(ROLES),
            form_error=form_error,
            form_ok=form_ok,
        ),
        status_code=400 if form_error else 200,
    )
