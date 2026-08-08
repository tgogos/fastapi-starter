"""HTML / HTMX routes for SQL items UI."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.auth.deps import get_or_create_csrf_token, require_user_html, verify_csrf
from app.db import items as items_repo
from app.web.paths import TEMPLATES_DIR

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _ctx(request: Request, user: dict, **extra):
    return {
        "request": request,
        "user": user,
        "csrf_token": get_or_create_csrf_token(request),
        **extra,
    }


@router.get("/items", response_class=HTMLResponse)
async def items_page(
    request: Request,
    user: dict = Depends(require_user_html),
):
    rows, total = await items_repo.list_items(page=1, size=100)
    return templates.TemplateResponse(
        request,
        "items.html",
        _ctx(request, user, items=rows, total=total),
    )


@router.post("/items", response_class=HTMLResponse, dependencies=[Depends(verify_csrf)])
async def create_item(
    request: Request,
    user: dict = Depends(require_user_html),
    name: str = Form(...),
    description: str = Form(""),
):
    name = name.strip()
    description = description.strip() or None
    if not name:
        rows, total = await items_repo.list_items(page=1, size=100)
        return templates.TemplateResponse(
            request,
            "partials/items_table.html",
            _ctx(request, user, items=rows, total=total, form_error="Name is required."),
            status_code=400,
        )

    await items_repo.create_item(name, description)
    rows, total = await items_repo.list_items(page=1, size=100)
    return templates.TemplateResponse(
        request,
        "partials/items_table.html",
        _ctx(request, user, items=rows, total=total),
    )


@router.get("/items/{item_id}/edit", response_class=HTMLResponse)
async def edit_item_form(
    request: Request,
    item_id: str,
    user: dict = Depends(require_user_html),
):
    item = await items_repo.get_item(item_id)
    if item is None:
        return HTMLResponse("Item not found", status_code=404)
    return templates.TemplateResponse(
        request,
        "partials/item_edit_row.html",
        _ctx(request, user, item=item),
    )


@router.get("/items/{item_id}/row", response_class=HTMLResponse)
async def item_row(
    request: Request,
    item_id: str,
    user: dict = Depends(require_user_html),
):
    item = await items_repo.get_item(item_id)
    if item is None:
        return HTMLResponse("Item not found", status_code=404)
    return templates.TemplateResponse(
        request,
        "partials/item_row.html",
        _ctx(request, user, item=item),
    )


@router.put("/items/{item_id}", response_class=HTMLResponse, dependencies=[Depends(verify_csrf)])
async def update_item(
    request: Request,
    item_id: str,
    user: dict = Depends(require_user_html),
    name: str = Form(...),
    description: str = Form(""),
):
    name = name.strip()
    description = description.strip() or None
    item = await items_repo.update_item(
        item_id,
        name=name,
        description=description,
        description_set=True,
    )
    if item is None:
        return HTMLResponse("Item not found", status_code=404)
    return templates.TemplateResponse(
        request,
        "partials/item_row.html",
        _ctx(request, user, item=item),
    )


@router.delete("/items/{item_id}", response_class=HTMLResponse, dependencies=[Depends(verify_csrf)])
async def delete_item(
    request: Request,
    item_id: str,
    user: dict = Depends(require_user_html),
):
    await items_repo.delete_item(item_id)
    rows, total = await items_repo.list_items(page=1, size=100)
    return templates.TemplateResponse(
        request,
        "partials/items_table.html",
        _ctx(request, user, items=rows, total=total),
    )
