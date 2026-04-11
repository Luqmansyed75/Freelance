"""
Page router — serves all HTML pages via Jinja2 templates.
Auth state is read from the HTTP-only 'access_token' cookie.
"""
import os
from typing import Optional

from fastapi import APIRouter, Request, Cookie, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from backend.db.deps import get_db
from backend.core.config import settings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

router = APIRouter(tags=["Pages"])


def _get_user_from_cookie(request: Request, db: Session) -> Optional[object]:
    """Decode JWT from cookie and return the user, or None."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            return None
        from backend.crud.user import get_user_by_email
        return get_user_by_email(db, email=email)
    except JWTError:
        return None


# ── Landing Page ──
@router.get("/", response_class=HTMLResponse)
def landing(request: Request, db: Session = Depends(get_db)):
    user = _get_user_from_cookie(request, db)
    return templates.TemplateResponse(request=request, name="landing.html", context={
        "request": request,
        "user": user,
    })


# ── Login Page ──
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    user = _get_user_from_cookie(request, db)
    if user:
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse(request=request, name="login.html", context={
        "request": request,
        "user": None,
        "error": None,
    })


# ── Signup Page ──
@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request, db: Session = Depends(get_db)):
    user = _get_user_from_cookie(request, db)
    if user:
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse(request=request, name="signup.html", context={
        "request": request,
        "user": None,
        "error": None,
    })


# ── Dashboard Page (Protected) ──
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = _get_user_from_cookie(request, db)
    if not user:
        return RedirectResponse("/login?next=/dashboard", status_code=302)

    # Common skills for the selector
    SKILL_TAGS = [
        "Python", "JavaScript", "TypeScript", "React", "Vue.js", "Angular",
        "Node.js", "FastAPI", "Django", "Flask", "Express",
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
        "Docker", "Kubernetes", "AWS", "GCP", "Azure",
        "Machine Learning", "Data Science", "NLP", "Computer Vision",
        "GraphQL", "REST API", "WebSockets",
        "React Native", "Flutter", "Swift", "Kotlin",
        "Go", "Rust", "Java", "PHP", "Ruby on Rails",
        "DevOps", "CI/CD", "Git", "Linux", "Terraform",
        "UI/UX", "Figma", "WordPress", "Shopify", "SEO",
        "Content Writing", "Copywriting", "Video Editing", "3D Modeling",
    ]

    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "request": request,
        "user": user,
        "skill_tags": SKILL_TAGS,
    })


# ── Applications CRM Page (Protected) ──
@router.get("/applications", response_class=HTMLResponse)
def applications_page(request: Request, db: Session = Depends(get_db)):
    user = _get_user_from_cookie(request, db)
    if not user:
        return RedirectResponse("/login?next=/applications", status_code=302)

    from backend.crud.application import get_user_applications
    from backend.schemas.application import ApplicationResponse

    apps = get_user_applications(db, user_id=user.id)
    app_data = [ApplicationResponse.from_db_model(a) for a in apps]

    return templates.TemplateResponse(request=request, name="applications.html", context={
        "request": request,
        "user": user,
        "applications": app_data,
    })
