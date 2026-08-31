# 1. Standard Library Imports
import os
from typing import Any, Generator  # noqa: UP035

# 2. Third-Party Imports
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# ── Configuration & Setup ──────────────────────────────────────────────────────

# Load environment variables (like your Postgres URL)
load_dotenv()

# We look for a DATABASE_URL in your .env file. 
# If it's not there, we safely fall back to a local SQLite file for easy testing.
SQLALCHEMY_DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ibm_hr_assistant.db")

# ── Database Engine ────────────────────────────────────────────────────────────

# Create the Engine (The actual connection to the hard drive/cloud)
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # SQLite needs this special flag so multiple API requests don't lock it up
    engine: Engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL with Neon-safe connection pool settings:
    # - pool_pre_ping: tests the connection before use; silently reconnects if
    #   Neon has suspended the instance (fixes the "server closed the connection" error)
    # - pool_recycle: discard connections older than 5 min so we never hold a
    #   stale socket across a Neon suspend/resume cycle
    # - pool_timeout: raise immediately rather than hanging if no connection is free
    # - connect_args sslmode: Neon requires SSL
    engine: Engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_timeout=30,
        connect_args={"sslmode": "require"},
    )

# Create a Session Factory (This hands out safe, temporary connections to your endpoints)
SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
class Base(DeclarativeBase):
    pass


# ── FastAPI Dependencies ───────────────────────────────────────────────────────

# The Dependency: Every time an API route needs the database, it uses this to get a secure session
def get_db() -> Generator[Session, Any, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()