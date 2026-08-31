"""
test_auth.py — Integration tests for /auth/register and /auth/login.
"""

import pytest
from tests.conftest import login_user, register_user


class TestRegister:
    def test_register_success(self, client):
        resp = register_user(client)
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "alice"
        assert data["role"] == "new_hire"
        assert data["department"] == "Engineering"
        assert "id" in data
        # password must never be returned
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client):
        register_user(client)
        resp = register_user(client)
        assert resp.status_code == 400

    def test_register_default_role(self, client):
        resp = client.post("/auth/register", json={
            "username": "bob",
            "password": "pass1234",
        })
        assert resp.status_code == 201
        assert resp.json()["role"] == "new_hire"

    def test_register_custom_role(self, client):
        resp = register_user(client, role="hr_admin")
        assert resp.status_code == 201
        assert resp.json()["role"] == "hr_admin"


class TestLogin:
    def test_login_success(self, client):
        register_user(client)
        resp = login_user(client)
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        register_user(client)
        resp = client.post("/auth/login", json={
            "username": "alice",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    def test_login_unknown_user(self, client):
        resp = login_user(client, username="nobody")
        assert resp.status_code == 401

    def test_login_returns_jwt(self, client):
        register_user(client)
        resp = login_user(client)
        token = resp.json()["access_token"]
        # JWT has 3 dot-separated base64 segments
        assert token.count(".") == 2
