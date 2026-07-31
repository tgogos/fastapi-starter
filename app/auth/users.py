"""User queries against SQLite."""

from __future__ import annotations

from typing import Any, Optional

from app.db.connection import get_connection


async def get_user_by_id(user_id: int) -> Optional[dict[str, Any]]:
    conn = get_connection()
    async with conn.execute(
        "SELECT id, username, password_hash, created_at FROM users WHERE id = ?",
        (user_id,),
    ) as cursor:
        row = await cursor.fetchone()
    if row is None:
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "password_hash": row["password_hash"],
        "created_at": row["created_at"],
    }


async def get_user_by_username(username: str) -> Optional[dict[str, Any]]:
    conn = get_connection()
    async with conn.execute(
        "SELECT id, username, password_hash, created_at FROM users WHERE username = ?",
        (username,),
    ) as cursor:
        row = await cursor.fetchone()
    if row is None:
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "password_hash": row["password_hash"],
        "created_at": row["created_at"],
    }


async def count_users() -> int:
    conn = get_connection()
    async with conn.execute("SELECT COUNT(*) AS c FROM users") as cursor:
        row = await cursor.fetchone()
    return int(row["c"])


async def create_user(username: str, password_hash: str) -> dict[str, Any]:
    conn = get_connection()
    cursor = await conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    await conn.commit()
    user = await get_user_by_id(cursor.lastrowid)
    assert user is not None
    return user
