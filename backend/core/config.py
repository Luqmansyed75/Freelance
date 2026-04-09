"""
Application settings loaded from .env file.
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # ── JWT ──
    SECRET_KEY: str = "change-me-to-a-random-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Database ──
    DATABASE_URL: str = "sqlite:///./data/freelancing.db"

    # ── Admin ──
    ADMIN_EMAIL: str = "admin@freelancing.com"

    # ── Google AI ──
    GOOGLE_API_KEY: str = ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
