"""
CRUD operations for User model.
"""
from typing import Optional

from sqlalchemy.orm import Session

from backend.models.user import User
from backend.core.security import hash_password, verify_password
from backend.core.config import settings


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Fetch a user by email address."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Fetch a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, password: str) -> User:
    """
    Create a new user with hashed password.
    Automatically grants admin if email matches ADMIN_EMAIL from settings.
    """
    is_admin = email.lower() == settings.ADMIN_EMAIL.lower()

    user = User(
        email=email.lower().strip(),
        hashed_password=hash_password(password),
        is_admin=is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Verify credentials and return the user, or None if invalid."""
    user = get_user_by_email(db, email=email.lower().strip())
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
