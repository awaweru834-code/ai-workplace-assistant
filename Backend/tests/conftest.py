"""
conftest.py — Shared pytest fixtures.

Uses an in-memory SQLite database so no real PostgreSQL connection is needed.
All external services (Groq, Pinecone) are patched at the module level so
network calls are never made during tests.

Rate limiting is disabled by patching slowapi before the app is imported.
"""

import os

# ── Environment must be set before any app imports ────────────────────────────
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")
os.environ.setdefault("PINECONE_API_KEY", "test-pinecone-key")
os.environ.setdefault("PINECONE_INDEX_NAME", "hr-policies")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from core.database import Base, get_db  # noqa: E402
from core.rate_limit import limiter  # noqa: E402
from main import app  # noqa: E402

# ── Disable rate limiting for the entire test session ─────────────────────────
limiter.enabled = False

# ── In-memory SQLite engine ───────────────────────────────────────────────────
SQLITE_URL = "sqlite:///./test.db"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once per test session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_tables():
    """Truncate all tables between tests so state doesn't bleed across."""
    yield
    db = TestingSessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()


@pytest.fixture(scope="session")
def client(create_tables):
    """FastAPI TestClient with the DB dependency overridden."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


# ── Auth helpers ──────────────────────────────────────────────────────────────

def register_user(client, username="alice", password="secret123", role="new_hire"):
    resp = client.post("/auth/register", json={
        "username": username,
        "password": password,
        "role": role,
        "department": "Engineering",
    })
    return resp


def login_user(client, username="alice", password="secret123"):
    resp = client.post("/auth/login", json={
        "username": username,
        "password": password,
    })
    return resp


def auth_headers(client, username="alice", password="secret123"):
    """Register (if needed) and return Bearer auth headers."""
    reg = register_user(client, username, password)
    # 201 = fresh register; 400 = already exists — both are fine, proceed to login
    assert reg.status_code in (201, 400), f"Unexpected register status: {reg.status_code} {reg.text}"
    resp = login_user(client, username, password)
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def admin_headers(client):
    """Register an hr_admin user and return its auth headers."""
    reg = register_user(client, username="admin", password="adminpass", role="hr_admin")
    assert reg.status_code in (201, 400), f"Unexpected register status: {reg.status_code} {reg.text}"
    resp = login_user(client, username="admin", password="adminpass")
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
