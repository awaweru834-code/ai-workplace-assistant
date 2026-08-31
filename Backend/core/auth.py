# 1. Standard Library Imports
import os
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Annotated

# 2. Third-Party Imports
import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

# 3. Local Application Imports
from .database import get_db
from .models import User

# Load .env before reading any env vars
load_dotenv()

# ── Configuration & Setup ──────────────────────────────────────────────────────

SECRET_KEY: str = os.getenv("SECRET_KEY", "test-secret-key-for-validation-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ── Password Hashing ───────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

# ── JWT Helpers ────────────────────────────────────────────────────────────────

def create_access_token(data: dict[str, object], expires_delta: timedelta | None = None) -> str:
    payload = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload.update({"exp": expire})
    return jwt.encode(claims=payload, key=SECRET_KEY, algorithm=ALGORITHM)

# ── FastAPI Dependencies ───────────────────────────────────────────────────────

_TokenDep = Annotated[str, Depends(oauth2_scheme)]
_DbDep = Annotated[Session, Depends(get_db)]

def get_token_payload(token: _TokenDep) -> dict[str, object]:
    """Step 1: Decode the token, handle JWT errors, and extract the payload."""
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise exc

    if not payload or payload.get("sub") is None:
        raise exc
    
    return payload

def get_current_user(payload: Annotated[dict[str, object], Depends(get_token_payload)], db: _DbDep) -> User:
    """Step 2: Validate the payload against the database."""
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    
    if user is None or user.is_active is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive or not found.")
    return user

def require_role(*roles: str) -> Callable[..., User]:
    """Dependency factory for RBAC that checks roles BEFORE hitting the database."""
    def _guard(payload: Annotated[dict[str, object], Depends(get_token_payload)], db: _DbDep) -> User:
        if payload.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(roles)}.",
            )
        return get_current_user(payload, db)
    return _guard