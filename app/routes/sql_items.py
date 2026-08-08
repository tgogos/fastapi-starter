"""JSON CRUD for SQLite-backed items (mounted at /api/sql-items)."""

from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.deps import require_user
from app.db import items as items_repo
from app.models.sql_item import (
    PaginatedSqlItems,
    SqlItemCreate,
    SqlItemResponse,
    SqlItemUpdate,
)

router = APIRouter()


def _parse_response(row: dict) -> SqlItemResponse:
    return SqlItemResponse(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.post(
    "/",
    response_model=SqlItemResponse,
    status_code=201,
    summary="Create a SQL item",
)
async def create_sql_item(
    item: SqlItemCreate,
    _user: dict = Depends(require_user),
) -> SqlItemResponse:
    row = await items_repo.create_item(item.name, item.description)
    return _parse_response(row)


@router.get(
    "/",
    response_model=PaginatedSqlItems,
    summary="List SQL items",
)
async def list_sql_items(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
) -> PaginatedSqlItems:
    rows, total = await items_repo.list_items(page=page, size=size)
    return PaginatedSqlItems(
        items=[_parse_response(r) for r in rows],
        total_count=total,
        page=page,
        size=size,
        total_pages=ceil(total / size) if total else 0,
    )


@router.get(
    "/search/",
    response_model=PaginatedSqlItems,
    summary="Search SQL items by name",
)
async def search_sql_items(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
) -> PaginatedSqlItems:
    rows, total = await items_repo.search_items(q, page=page, size=size)
    return PaginatedSqlItems(
        items=[_parse_response(r) for r in rows],
        total_count=total,
        page=page,
        size=size,
        total_pages=ceil(total / size) if total else 0,
    )


@router.get(
    "/{item_id}",
    response_model=SqlItemResponse,
    summary="Get a SQL item",
)
async def get_sql_item(item_id: str) -> SqlItemResponse:
    row = await items_repo.get_item(item_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return _parse_response(row)


@router.put(
    "/{item_id}",
    response_model=SqlItemResponse,
    summary="Update a SQL item",
)
async def update_sql_item(
    item_id: str,
    item_update: SqlItemUpdate,
    _user: dict = Depends(require_user),
) -> SqlItemResponse:
    data = item_update.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    row = await items_repo.update_item(
        item_id,
        name=data.get("name"),
        description=data.get("description"),
        description_set="description" in data,
    )
    if row is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return _parse_response(row)


@router.delete(
    "/{item_id}",
    status_code=204,
    summary="Delete a SQL item",
)
async def delete_sql_item(
    item_id: str,
    _user: dict = Depends(require_user),
) -> None:
    deleted = await items_repo.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
