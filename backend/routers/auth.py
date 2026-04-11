"""
Authentication router — register, login, profile, and cookie-based page auth endpoints.
"""
import os
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from backend.db.deps import get_db
from backend.schemas.user import UserCreate, UserResponse, Token
from backend.crud.user import get_user_by_email, create_user, authenticate_user
from backend.core.security import create_access_token, get_current_user

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "backend", "templates"))

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── JSON API endpoints (for API clients) ──

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
    """OAuth2-compatible login. Returns JWT access token."""
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


# ── Cookie-based page form handlers ──

@router.post("/login-page", response_class=HTMLResponse)
def login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Handle login form submission. Sets JWT cookie on success."""
    user = authenticate_user(db, email=email, password=password)
    if not user:
        return templates.TemplateResponse(request=request, name="login.html", context={
            "request": request,
            "user": None,
            "error": "Invalid email or password. Please try again.",
        }, status_code=401)

    token = create_access_token(data={"sub": user.email})
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,  # 7 days
        samesite="lax",
    )
    return response


@router.post("/register-page", response_class=HTMLResponse)
def register_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Handle signup form submission. Creates user and sets JWT cookie."""
    if password != confirm_password:
        return templates.TemplateResponse(request=request, name="signup.html", context={
            "request": request,
            "user": None,
            "error": "Passwords do not match.",
        }, status_code=400)

    if len(password) < 8:
        return templates.TemplateResponse(request=request, name="signup.html", context={
            "request": request,
            "user": None,
            "error": "Password must be at least 8 characters.",
        }, status_code=400)

    existing = get_user_by_email(db, email=email.lower().strip())
    if existing:
        return templates.TemplateResponse(request=request, name="signup.html", context={
            "request": request,
            "user": None,
            "error": "An account with this email already exists.",
        }, status_code=409)

    user = create_user(db, email=email.lower().strip(), password=password)
    token = create_access_token(data={"sub": user.email})
    response = RedirectResponse("/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax",
    )
    return response


@router.get("/logout")
def logout():
    """Clear the auth cookie and redirect to landing page."""
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token")
    return response
