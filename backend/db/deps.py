"""
FastAPI dependency for database sessions.
"""
from typing import Generator

from backend.db.engine import SessionLocal


def get_db() -> Generator:
    """Yield a SQLAlchemy session, ensuring it's closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
