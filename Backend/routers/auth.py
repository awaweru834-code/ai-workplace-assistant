from core.auth import create_access_token, hash_password, verify_password
from core.database import get_db
from core.models import TokenResponse, User, UserCreate, UserResponse
from core.rate_limit import limiter
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new employee account",
)
@limiter.limit("10/minute")
def register(request: Request, payload: UserCreate, db: Session = Depends(get_db)):  # noqa: B008
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username is already taken.")

    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        department=payload.department,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# 2. Update your login route:
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Obtain a JWT Bearer token",
)
@limiter.limit("20/minute")
def login(
    request: Request, 
    form_data: OAuth2PasswordRequestForm = Depends(),  # noqa: B008
    db: Session = Depends(get_db)  # noqa: B008
):
    # 1. Find the user in the database
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # 2. Verify user exists and the password math matches
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Ensure the user's account hasn't been deactivated
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Account is deactivated."
        )

    # 4. Generate the JWT, embedding BOTH the user ID and their Role!
    token = create_access_token({
        "sub": str(user.id), 
        "role": user.role
    })
    
    return TokenResponse(access_token=token, token_type="bearer")