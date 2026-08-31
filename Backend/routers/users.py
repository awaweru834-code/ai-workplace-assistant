from core.auth import get_current_user, hash_password, require_role
from core.database import get_db
from core.models import User, UserCreate, UserResponse, UserUpdate
from core.rate_limit import limiter
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the authenticated user's profile",
)
@limiter.limit("60/minute")
def get_me(request: Request, current_user: User = Depends(get_current_user)):  # noqa: B008
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update name, department, or password",
)
@limiter.limit("20/minute")
def update_me(
    request: Request,
    payload: UserUpdate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.department is not None:
        current_user.department = payload.department
    if payload.password:
        current_user.hashed_password = hash_password(payload.password)

    db.commit()
    db.refresh(current_user)
    return current_user


# ── HR Admin only ─────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=list[UserResponse],
    summary="[HR Admin] List all users",
)
@limiter.limit("30/minute")
def list_users(
    request: Request,
    db: Session = Depends(get_db),  # noqa: B008
    _: User = Depends(require_role("hr_admin")),  # noqa: B008
):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    summary="[HR Admin] Deactivate a user account",
)
@limiter.limit("20/minute")
def deactivate_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    _: User = Depends(require_role("hr_admin")),  # noqa: B008
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user

@router.post(
    "/",
    response_model=UserResponse,
    summary="[HR Admin] Create a new user account",
)
@limiter.limit("20/minute")
@limiter.limit("20/minute")
def create_user(
    request: Request,
    payload: UserCreate, # Ensure this Pydantic model expects 'username' instead of 'email'
    db: Session = Depends(get_db),  # noqa: B008
    _: User = Depends(require_role("hr_admin")),  # noqa: B008
):
    # 1. Check if the username is already taken
    existing_user = db.query(User).filter(User.username == payload.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username is already registered.")

    # 2. Create the new user and hash the manually provided password
    new_user = User(
        username=payload.username, # Updated from email to username
        hashed_password=hash_password(payload.password),
        role=payload.role,
        is_active=True
    )
    
    # 3. Save to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user