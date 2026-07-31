"""Async SQLite connection management."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import aiosqlite

from app.core import config

_connection: Optional[aiosqlite.Connection] = None

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


async def connect_to_sqlite() -> aiosqlite.Connection:
    """Open SQLite, apply schema, and keep a process-wide connection."""
    global _connection

    db_path = config.sqlite_path_from_url()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    _connection = await aiosqlite.connect(db_path)
    _connection.row_factory = aiosqlite.Row
    await _connection.execute("PRAGMA foreign_keys = ON")

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    await _connection.executescript(schema_sql)
    await _connection.commit()

    print(f"✅ Connected to SQLite at {db_path}")
    return _connection


async def close_sqlite() -> None:
    """Close the SQLite connection."""
    global _connection
    if _connection is not None:
        await _connection.close()
        _connection = None
        print("🔌 SQLite connection closed")


def get_connection() -> aiosqlite.Connection:
    """Return the active SQLite connection."""
    if _connection is None:
        raise RuntimeError("SQLite not connected. Call connect_to_sqlite() first.")
    return _connection


async def check_sqlite_connection() -> bool:
    """Return True if SQLite responds to a simple query."""
    try:
        if _connection is None:
            return False
        async with _connection.execute("SELECT 1") as cursor:
            row = await cursor.fetchone()
        return row is not None
    except Exception:
        return False
