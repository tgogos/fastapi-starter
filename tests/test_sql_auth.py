"""Tests for /api/sql-items, API tokens, and browser auth."""

import os

from fastapi.testclient import TestClient

API_SQL = "/api/sql-items"


class TestSqlItemsApi:
    def test_list_empty(self, client: TestClient):
        response = client.get(f"{API_SQL}/")
        assert response.status_code == 200
        body = response.json()
        assert body["total_count"] == 0
        assert body["items"] == []

    def test_create_requires_auth(self, client: TestClient, sample_item_data: dict):
        response = client.post(f"{API_SQL}/", json=sample_item_data)
        assert response.status_code == 401

    def test_crud_flow_authenticated(
        self, auth_client: TestClient, sample_item_data: dict, sample_item_update_data: dict
    ):
        create = auth_client.post(f"{API_SQL}/", json=sample_item_data)
        assert create.status_code == 201
        item = create.json()
        item_id = item["id"]
        assert item["name"] == sample_item_data["name"]

        get_one = auth_client.get(f"{API_SQL}/{item_id}")
        assert get_one.status_code == 200
        assert get_one.json()["id"] == item_id

        update = auth_client.put(f"{API_SQL}/{item_id}", json=sample_item_update_data)
        assert update.status_code == 200
        assert update.json()["name"] == sample_item_update_data["name"]

        search = auth_client.get(
            f"{API_SQL}/search/?q={sample_item_update_data['name']}"
        )
        assert search.status_code == 200
        assert search.json()["total_count"] >= 1

        delete = auth_client.delete(f"{API_SQL}/{item_id}")
        assert delete.status_code == 204

        missing = auth_client.get(f"{API_SQL}/{item_id}")
        assert missing.status_code == 404


class TestApiAuth:
    def test_token_and_bearer_crud(
        self, client: TestClient, sample_item_data: dict
    ):
        bad = client.post(
            "/api/auth/token",
            json={"username": "nope", "password": "wrong"},
        )
        assert bad.status_code == 401

        token_resp = client.post(
            "/api/auth/token",
            json={
                "username": os.environ["DEMO_USERNAME"],
                "password": os.environ["DEMO_PASSWORD"],
            },
        )
        assert token_resp.status_code == 200
        token = token_resp.json()["access_token"]
        assert token_resp.json()["token_type"] == "bearer"
        headers = {"Authorization": f"Bearer {token}"}

        me = client.get("/api/auth/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["username"] == os.environ["DEMO_USERNAME"]

        create = client.post(f"{API_SQL}/", json=sample_item_data, headers=headers)
        assert create.status_code == 201
        item_id = create.json()["id"]

        delete = client.delete(f"{API_SQL}/{item_id}", headers=headers)
        assert delete.status_code == 204

        revoke = client.delete("/api/auth/token", headers=headers)
        assert revoke.status_code == 204

        me_after = client.get("/api/auth/me", headers=headers)
        assert me_after.status_code == 401

    def test_invalid_bearer_rejected(self, client: TestClient, sample_item_data: dict):
        response = client.post(
            f"{API_SQL}/",
            json=sample_item_data,
            headers={"Authorization": "Bearer not-a-real-token"},
        )
        assert response.status_code == 401

    def test_me_requires_auth(self, client: TestClient):
        assert client.get("/api/auth/me").status_code == 401

    def test_revoke_requires_bearer(self, client: TestClient):
        assert client.delete("/api/auth/token").status_code == 401


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
        # CSRF rotated on login — take the token from the UI page
        csrf = ui.text.split('name="csrf_token" value="', 1)[1].split('"', 1)[0]

        logout = client.post(
            "/auth/logout",
            data={"csrf_token": csrf},
            follow_redirects=False,
        )
        assert logout.status_code == 303

        again = client.get("/ui/items", follow_redirects=False)
        assert again.status_code == 303

    def test_login_rejects_bad_csrf(self, client: TestClient):
        client.get("/auth/login")  # establish session + CSRF
        response = client.post(
            "/auth/login",
            data={
                "username": os.environ["DEMO_USERNAME"],
                "password": os.environ["DEMO_PASSWORD"],
                "csrf_token": "not-the-real-token",
            },
            follow_redirects=False,
        )
        assert response.status_code == 403

    def test_get_logout_removed(self, client: TestClient):
        assert client.get("/auth/logout").status_code == 405


class TestHealthSqlite:
    def test_health_includes_sqlite(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert "sqlite_ping" in body
        assert body["sqlite_ping"] == "ok"


class TestRoot:
    def test_root_redirects_to_ui(self, client: TestClient):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/ui/items"
