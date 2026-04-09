"""
Pipeline runner service — wraps the existing pipeline.py for background execution.
"""
import logging
import os
import sys

logger = logging.getLogger("backend.pipeline_runner")


def run_pipeline_and_sync(session_factory):
    """
    Background task that:
      1. Runs the existing pipeline (scrape → clean → enrich → extract skills)
      2. Syncs the resulting final_jobs.json into the database

    Args:
        session_factory: SQLAlchemy sessionmaker to create a new session
                         (BackgroundTasks run outside the request lifecycle).
    """
    logger.info("Pipeline background task started.")

    # ── Step 1: Run the existing pipeline ──
    try:
        # Ensure the project root is on sys.path so pipeline imports work
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from pipeline import run_pipeline

        logger.info("Running data pipeline...")
        run_pipeline()
        logger.info("Pipeline completed successfully.")
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        return

    # ── Step 2: Sync results into the database ──
    try:
        from backend.crud.job import upsert_jobs_from_json

        final_jobs_path = os.path.join(project_root, "data", "final_jobs.json")
        db = session_factory()

        try:
            count = upsert_jobs_from_json(db, final_jobs_path)
            logger.info(f"Database sync complete: {count} jobs upserted.")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database sync failed: {e}", exc_info=True)
