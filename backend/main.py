"""
FastAPI application entry point.

Run with:
    uvicorn backend.main:app --reload
    or
    python -m uvicorn backend.main:app --reload
"""
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db.base import Base  # noqa: F401  — registers all models
from backend.db.engine import engine, SessionLocal
from backend.routers import auth, jobs, applications
from backend.crud.job import upsert_jobs_from_json

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("backend")

# ── FastAPI App ──
app = FastAPI(
    title="Freelance Job Matcher API",
    description=(
        "REST API backend for the AI-powered freelance job scraping and "
        "aggregation platform. Provides user authentication, enriched job "
        "data, and a personal CRM for job applications."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware (allow Streamlit and local frontends) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routers ──
API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(jobs.router, prefix=API_PREFIX)
app.include_router(applications.router, prefix=API_PREFIX)


# ── Startup Event ──
@app.on_event("startup")
def on_startup():
    """Create all database tables and load existing job data on first run."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready.")

    # Load existing final_jobs.json into the database if it exists
    final_jobs_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "final_jobs.json"
    )
    if os.path.exists(final_jobs_path):
        logger.info(f"Loading existing jobs from {final_jobs_path}...")
        db = SessionLocal()
        try:
            count = upsert_jobs_from_json(db, final_jobs_path)
            logger.info(f"Loaded {count} jobs into the database.")
        except Exception as e:
            logger.error(f"Failed to load jobs: {e}", exc_info=True)
        finally:
            db.close()
    else:
        logger.info("No existing final_jobs.json found, skipping initial load.")


# ── Health Check ──
@app.get("/", tags=["Health"])
def health_check():
    """Root health-check endpoint."""
    return {
        "status": "healthy",
        "service": "Freelance Job Matcher API",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
    }
