from contextlib import asynccontextmanager

from core.database import Base, engine
from core.rate_limit import limiter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, documents, hr_chat, users
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# ── Lifespan: create DB tables once on startup ────────────────────────────────

@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


# ── Application ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Corporate Onboarding & Policy Co-Worker",
    description=(
        "IBM AI Builders Challenge — Future of Work. "
        "A production-grade HR Assistant with JWT auth, RBAC, RAG (Pinecone), "
        "tool-calling (Groq Llama3), and stateless PostgreSQL chat memory."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── Rate limiting ──────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(exc_class_or_status_code=RateLimitExceeded, handler=_rate_limit_exceeded_handler)#type: ignore[arg-type]


# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(router=auth.router)
app.include_router(router=users.router)
app.include_router(router=hr_chat.router)
app.include_router(router=documents.router)



# ── Health ─────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    return {"status": "ok", "app": "AI HR Co-Worker API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    return {"status": "healthy"}
