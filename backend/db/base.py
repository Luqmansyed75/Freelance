"""
Central import point for the declarative Base.
Import all models here so Alembic and create_all() can discover them.
"""
from backend.db.engine import Base  # noqa: F401

# Import all models so they register with Base.metadata
from backend.models.user import User  # noqa: F401
from backend.models.job import Job  # noqa: F401
from backend.models.application import Application  # noqa: F401
