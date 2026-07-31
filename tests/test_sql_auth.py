"""Tests for SQLite-backed /sql-items API and auth-gated writes."""

import os

from fastapi.testclient import TestClient


class TestSqlItemsApi:
    def test_list_empty(self, client: TestClient):
        response = client.get("/sql-items/")
        assert response.status_code == 200
        body = response.json()
        assert body["total_count"] == 0
        assert body["items"] == []

    def test_create_requires_auth(self, client: TestClient, sample_item_data: dict):
        response = client.post("/sql-items/", json=sample_item_data)
        assert response.status_code == 401

    def test_crud_flow_authenticated(
        self, auth_client: TestClient, sample_item_data: dict, sample_item_update_data: dict
    ):
        create = auth_client.post("/sql-items/", json=sample_item_data)
        assert create.status_code == 201
        item = create.json()
        item_id = item["id"]
        assert item["name"] == sample_item_data["name"]

        get_one = auth_client.get(f"/sql-items/{item_id}")
        assert get_one.status_code == 200
        assert get_one.json()["id"] == item_id

        update = auth_client.put(f"/sql-items/{item_id}", json=sample_item_update_data)
        assert update.status_code == 200
        assert update.json()["name"] == sample_item_update_data["name"]

        search = auth_client.get(
            f"/sql-items/search/?q={sample_item_update_data['name']}"
        )
        assert search.status_code == 200
        assert search.json()["total_count"] >= 1

        delete = auth_client.delete(f"/sql-items/{item_id}")
        assert delete.status_code == 204

        missing = auth_client.get(f"/sql-items/{item_id}")
        assert missing.status_code == 404


class TestAuthWeb:
    def test_login_page_ok(self, client: TestClient):
        response = client.get("/auth/login")
        assert response.status_code == 200
        assert "Log in" in response.text

    def test_items_ui_redirects_when_anonymous(self, client: TestClient):
        response = client.get("/ui/items", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/auth/login"

    def test_items_ui_ok_when_authenticated(self, auth_client: TestClient):
        response = auth_client.get("/ui/items")
        assert response.status_code == 200
        assert "SQL items" in response.text

    def test_login_logout(self, client: TestClient):
        page = client.get("/auth/login")
        csrf = page.text.split('name="csrf_token" value="', 1)[1].split('"', 1)[0]
        login = client.post(
            "/auth/login",
            data={
                "username": os.environ["DEMO_USERNAME"],
                "password": os.environ["DEMO_PASSWORD"],
                "csrf_token": csrf,
            },
            follow_redirects=False,
        )
        assert login.status_code == 303

        ui = client.get("/ui/items")
        assert ui.status_code == 200

        logout = client.get("/auth/logout", follow_redirects=False)
        assert logout.status_code == 303

        again = client.get("/ui/items", follow_redirects=False)
        assert again.status_code == 303


class TestHealthSqlite:
    def test_health_includes_sqlite(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert "sqlite_ping" in body
        assert body["sqlite_ping"] == "ok"
