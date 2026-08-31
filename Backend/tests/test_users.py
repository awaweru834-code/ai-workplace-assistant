"""
test_users.py — Integration tests for /users endpoints.
"""

import pytest
from tests.conftest import admin_headers, auth_headers, register_user


class TestGetMe:
    def test_get_me_authenticated(self, client):
        headers = auth_headers(client)
        resp = client.get("/users/me", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "alice"
        assert data["role"] == "new_hire"

    def test_get_me_unauthenticated(self, client):
        resp = client.get("/users/me")
        assert resp.status_code == 401

    def test_get_me_invalid_token(self, client):
        resp = client.get("/users/me", headers={"Authorization": "Bearer notavalidtoken"})
        assert resp.status_code == 401


class TestUpdateMe:
    def test_update_department(self, client):
        headers = auth_headers(client)
        resp = client.patch("/users/me", json={"department": "Finance"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["department"] == "Finance"

    def test_update_password(self, client):
        headers = auth_headers(client)
        resp = client.patch("/users/me", json={"password": "newpass999"}, headers=headers)
        assert resp.status_code == 200
        # Verify new password works
        login_resp = client.post("/auth/login", json={
            "username": "alice", "password": "newpass999"
        })
        assert login_resp.status_code == 200

    def test_update_unauthenticated(self, client):
        resp = client.patch("/users/me", json={"department": "Finance"})
        assert resp.status_code == 401


class TestAdminEndpoints:
    def test_list_users_as_admin(self, client):
        headers = admin_headers(client)
        resp = client.get("/users/", headers=headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_users_as_regular_user(self, client):
        headers = auth_headers(client)
        resp = client.get("/users/", headers=headers)
        assert resp.status_code == 403

    def test_list_users_unauthenticated(self, client):
        resp = client.get("/users/")
        assert resp.status_code == 401

    def test_deactivate_user(self, client):
        # Register a target user
        register_user(client, username="target", password="pass1234")
        # Get target's id
        admin_hdrs = admin_headers(client)
        users = client.get("/users/", headers=admin_hdrs).json()
        target = next(u for u in users if u["username"] == "target")

        resp = client.patch(f"/users/{target['id']}/deactivate", headers=admin_hdrs)
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

    def test_deactivate_nonexistent_user(self, client):
        headers = admin_headers(client)
        resp = client.patch("/users/99999/deactivate", headers=headers)
        assert resp.status_code == 404
