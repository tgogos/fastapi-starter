"""SQL helpers for sql_items table."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from app.db.connection import get_connection


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _row_to_dict(row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


async def create_item(name: str, description: Optional[str] = None) -> dict[str, Any]:
    conn = get_connection()
    item_id = str(uuid4())
    now = _utcnow()
    await conn.execute(
        """
        INSERT INTO sql_items (id, name, description, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (item_id, name, description, now, now),
    )
    await conn.commit()
    return await get_item(item_id)  # type: ignore[return-value]


async def get_item(item_id: str) -> Optional[dict[str, Any]]:
    conn = get_connection()
    async with conn.execute(
        "SELECT id, name, description, created_at, updated_at FROM sql_items WHERE id = ?",
        (item_id,),
    ) as cursor:
        row = await cursor.fetchone()
    return _row_to_dict(row) if row else None


async def list_items(page: int = 1, size: int = 10) -> tuple[list[dict[str, Any]], int]:
    conn = get_connection()
    async with conn.execute("SELECT COUNT(*) AS c FROM sql_items") as cursor:
        total = int((await cursor.fetchone())["c"])

    offset = (page - 1) * size
    async with conn.execute(
        """
        SELECT id, name, description, created_at, updated_at
        FROM sql_items
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """,
        (size, offset),
    ) as cursor:
        rows = await cursor.fetchall()

    return [_row_to_dict(r) for r in rows], total


async def search_items(
    query: str, page: int = 1, size: int = 10
) -> tuple[list[dict[str, Any]], int]:
    conn = get_connection()
    like = f"%{query}%"
    async with conn.execute(
        "SELECT COUNT(*) AS c FROM sql_items WHERE name LIKE ? COLLATE NOCASE",
        (like,),
    ) as cursor:
        total = int((await cursor.fetchone())["c"])

    offset = (page - 1) * size
    async with conn.execute(
        """
        SELECT id, name, description, created_at, updated_at
        FROM sql_items
        WHERE name LIKE ? COLLATE NOCASE
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """,
        (like, size, offset),
    ) as cursor:
        rows = await cursor.fetchall()

    return [_row_to_dict(r) for r in rows], total


async def update_item(
    item_id: str,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    description_set: bool = False,
) -> Optional[dict[str, Any]]:
    existing = await get_item(item_id)
    if existing is None:
        return None

    new_name = name if name is not None else existing["name"]
    if description_set:
        new_description = description
    else:
        new_description = existing["description"] if description is None else description

    now = _utcnow()
    conn = get_connection()
    await conn.execute(
        """
        UPDATE sql_items
        SET name = ?, description = ?, updated_at = ?
        WHERE id = ?
        """,
        (new_name, new_description, now, item_id),
    )
    await conn.commit()
    return await get_item(item_id)


async def delete_item(item_id: str) -> bool:
    conn = get_connection()
    cursor = await conn.execute("DELETE FROM sql_items WHERE id = ?", (item_id,))
    await conn.commit()
    return cursor.rowcount > 0


async def clear_items() -> None:
    """Delete all sql_items (test helper)."""
    conn = get_connection()
    await conn.execute("DELETE FROM sql_items")
    await conn.commit()
