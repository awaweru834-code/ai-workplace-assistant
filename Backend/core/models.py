from datetime import datetime, timezone

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from core.database import Base

# ── SQLAlchemy Tables (Database) ───────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    __allow_unmapped__ = True

    id               = Column(Integer, primary_key=True, index=True)
    username         = Column(String, unique=True, index=True)
    email            = Column(String, unique=True, index=True, nullable=True)
    full_name        = Column(String, nullable=True)
    hashed_password  = Column(String)
    role             = Column(String, default="new_hire")
    department       = Column(String, default="General")
    is_active        = Column(Boolean, default=True)
    created_at       = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    tasks: list["OnboardingTask"] = relationship("OnboardingTask", back_populates="owner")


class OnboardingTask(Base):
    __tablename__ = "onboarding_tasks"
    __allow_unmapped__ = True

    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String, index=True)
    is_completed = Column(Boolean, default=False)
    user_id      = Column(Integer, ForeignKey("users.id"))

    owner: "User" = relationship("User", back_populates="tasks")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __allow_unmapped__ = True

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    session    = Column(String, default="hr-chat")   # 'hr-chat' | 'ask-pdf'
    role       = Column(String)                       # 'user' | 'assistant'
    content    = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ── Pydantic Schemas (API JSON Validation) ─────────────────────────────────────

class ChatRequest(BaseModel):
    message: str

class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    session: str

    class Config:
        from_attributes = True

# --- User & Auth Schemas ---

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "new_hire"
    

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    department: str
    is_active: bool
    email: str | None = None
    full_name: str | None = None

    class Config:
        from_attributes = True



class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserUpdate(BaseModel):
    full_name:  str | None = None
    password:   str | None = None
    role:       str | None = None
    department: str | None = None

