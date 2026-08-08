"""Pytest fixtures.

Sets test env vars before importing the app so Settings pick them up.
Requires MongoDB (same as existing suite; use `make test` via compose).
"""
import os
import sqlite3
from pathlib import Path

# Must run before app/core.config import side effects
_TEST_DB = Path(__file__).resolve().parent / ".test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest"
os.environ["DEBUG"] = "false"
os.environ.setdefault("DEMO_USERNAME", "admin")
os.environ.setdefault("DEMO_PASSWORD", "admin123")
os.environ.setdefault("MONGO_HOST", "mongodb")

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes.items import items_storage


@pytest.fixture
def client():
    """Test client with lifespan (Mongo + SQLite startup)."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clear_items_storage():
    """Clear in-memory items between tests."""
    items_storage.clear()
    yield
    items_storage.clear()


@pytest.fixture(autouse=True)
def clear_sql_items(client):
    """Clear SQLite sql_items between tests (keep seeded users)."""
    db_path = Path(os.environ["DATABASE_URL"].removeprefix("sqlite:///"))
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM sql_items")
    conn.commit()
    conn.close()
    yield
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM sql_items")
    conn.commit()
    conn.close()


@pytest.fixture
def sample_item_data():
    return {
        "name": "Test Item",
        "description": "A test item for testing purposes",
    }


@pytest.fixture
def sample_item_update_data():
    return {
        "name": "Updated Test Item",
        "description": "An updated test item",
    }


@pytest.fixture
def auth_client(client: TestClient):
    """Client logged in as the demo user (session cookie)."""
    login_page = client.get("/auth/login")
    assert login_page.status_code == 200
    html = login_page.text
    marker = 'name="csrf_token" value="'
    assert marker in html
    csrf = html.split(marker, 1)[1].split('"', 1)[0]

    response = client.post(
        "/auth/login",
        data={
            "username": os.environ["DEMO_USERNAME"],
            "password": os.environ["DEMO_PASSWORD"],
            "csrf_token": csrf,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    return client


def session_csrf_headers(client: TestClient) -> dict[str, str]:
    """CSRF header for session-authenticated JSON/API calls (from UI meta tag)."""
    page = client.get("/ui/items")
    assert page.status_code == 200
    marker = 'name="csrf-token" content="'
    assert marker in page.text
    token = page.text.split(marker, 1)[1].split('"', 1)[0]
    return {"X-CSRF-Token": token}
