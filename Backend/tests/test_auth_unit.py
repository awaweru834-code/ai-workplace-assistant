"""
test_auth_unit.py — Pure unit tests for core/auth.py helper functions.
No DB or HTTP layer involved.
"""

import time
from datetime import timedelta

import pytest
from jose import jwt

import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")

from core.auth import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = hash_password("mysecret")
        assert hashed != "mysecret"

    def test_verify_correct_password(self):
        hashed = hash_password("mysecret")
        assert verify_password("mysecret", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("mysecret")
        assert verify_password("wrongpass", hashed) is False

    def test_same_password_produces_different_hashes(self):
        """bcrypt uses a random salt — two hashes of the same password differ."""
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2
        # But both verify correctly
        assert verify_password("same", h1)
        assert verify_password("same", h2)


class TestCreateAccessToken:
    def test_token_is_decodable(self):
        token = create_access_token({"sub": "42"})
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "42"

    def test_token_contains_expiry(self):
        token = create_access_token({"sub": "1"})
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload

    def test_custom_expiry_is_respected(self):
        delta = timedelta(hours=2)
        before = time.time()
        token = create_access_token({"sub": "1"}, expires_delta=delta)
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        after = time.time()
        # exp should be ~2 hours from now (within a 5-second tolerance)
        expected_min = before + delta.total_seconds() - 5
        expected_max = after  + delta.total_seconds() + 5
        assert expected_min <= payload["exp"] <= expected_max

    def test_short_lived_token_expires(self):
        token = create_access_token({"sub": "1"}, expires_delta=timedelta(seconds=-1))
        with pytest.raises(Exception):  # jose raises ExpiredSignatureError
            jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
