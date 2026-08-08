"""SQL helpers for the books table."""

from __future__ import annotations

from datetime import datetime, timezone
from math import ceil
from typing import Any, Optional
from uuid import uuid4

from app.db.connection import get_connection


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _row_to_dict(row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "author": row["author"],
        "year": row["year"],
        "notes": row["notes"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


async def create_book(
    title: str,
    author: str,
    year: Optional[int] = None,
    notes: Optional[str] = None,
) -> dict[str, Any]:
    conn = get_connection()
    book_id = str(uuid4())
    now = _utcnow()
    await conn.execute(
        """
        INSERT INTO books (id, title, author, year, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (book_id, title, author, year, notes, now, now),
    )
    await conn.commit()
    return await get_book(book_id)  # type: ignore[return-value]


async def get_book(book_id: str) -> Optional[dict[str, Any]]:
    conn = get_connection()
    async with conn.execute(
        """
        SELECT id, title, author, year, notes, created_at, updated_at
        FROM books WHERE id = ?
        """,
        (book_id,),
    ) as cursor:
        row = await cursor.fetchone()
    return _row_to_dict(row) if row else None


async def list_books(
    page: int = 1,
    size: int = 10,
    q: Optional[str] = None,
) -> tuple[list[dict[str, Any]], int]:
    conn = get_connection()
    q = (q or "").strip() or None

    if q:
        like = f"%{q}%"
        async with conn.execute(
            """
            SELECT COUNT(*) AS c FROM books
            WHERE title LIKE ? COLLATE NOCASE
               OR author LIKE ? COLLATE NOCASE
            """,
            (like, like),
        ) as cursor:
            total = int((await cursor.fetchone())["c"])

        offset = (page - 1) * size
        async with conn.execute(
            """
            SELECT id, title, author, year, notes, created_at, updated_at
            FROM books
            WHERE title LIKE ? COLLATE NOCASE
               OR author LIKE ? COLLATE NOCASE
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (like, like, size, offset),
        ) as cursor:
            rows = await cursor.fetchall()
    else:
        async with conn.execute("SELECT COUNT(*) AS c FROM books") as cursor:
            total = int((await cursor.fetchone())["c"])

        offset = (page - 1) * size
        async with conn.execute(
            """
            SELECT id, title, author, year, notes, created_at, updated_at
            FROM books
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (size, offset),
        ) as cursor:
            rows = await cursor.fetchall()

    return [_row_to_dict(r) for r in rows], total


def total_pages(total: int, size: int) -> int:
    return ceil(total / size) if total else 0


async def update_book(
    book_id: str,
    *,
    title: Optional[str] = None,
    author: Optional[str] = None,
    year: Optional[int] = None,
    year_set: bool = False,
    notes: Optional[str] = None,
    notes_set: bool = False,
) -> Optional[dict[str, Any]]:
    existing = await get_book(book_id)
    if existing is None:
        return None

    new_title = title if title is not None else existing["title"]
    new_author = author if author is not None else existing["author"]
    if year_set:
        new_year = year
    else:
        new_year = existing["year"] if year is None else year
    if notes_set:
        new_notes = notes
    else:
        new_notes = existing["notes"] if notes is None else notes

    now = _utcnow()
    conn = get_connection()
    await conn.execute(
        """
        UPDATE books
        SET title = ?, author = ?, year = ?, notes = ?, updated_at = ?
        WHERE id = ?
        """,
        (new_title, new_author, new_year, new_notes, now, book_id),
    )
    await conn.commit()
    return await get_book(book_id)


async def delete_book(book_id: str) -> bool:
    conn = get_connection()
    cursor = await conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    await conn.commit()
    return cursor.rowcount > 0


async def clear_books() -> None:
    """Delete all books (test helper)."""
    conn = get_connection()
    await conn.execute("DELETE FROM books")
    await conn.commit()
