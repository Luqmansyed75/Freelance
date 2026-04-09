"""
Authentication router — register, login, and profile endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.db.deps import get_db
from backend.schemas.user import UserCreate, UserResponse, Token
from backend.crud.user import get_user_by_email, create_user, authenticate_user
from backend.core.security import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account. Returns 409 if email already exists."""
    existing = get_user_by_email(db, email=user_in.email.lower().strip())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )
    user = create_user(db, email=user_in.email, password=user_in.password)
    return user


@router.post(
    "/token",
    response_model=Token,
    summary="Login and get JWT token",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2-compatible login endpoint.
    Accepts 'username' (email) and 'password' via form data.
    Returns a JWT access token.
    """
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": user.email})
    return Token(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
def get_me(current_user=Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return current_user
