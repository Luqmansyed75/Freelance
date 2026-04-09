"""
Jobs router — list, detail, and pipeline trigger endpoints.
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session

from backend.db.deps import get_db
from backend.schemas.job import JobResponse, JobListResponse, PipelineTriggerResponse
from backend.crud.job import get_jobs, get_job_by_id
from backend.core.security import get_current_admin_user

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get(
    "",
    response_model=JobListResponse,
    summary="List all enriched jobs",
)
def list_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    source: Optional[str] = Query(None, description="Filter by source (e.g. 'working_nomads', 'wwr')"),
    skills: Optional[str] = Query(None, description="Comma-separated skills to filter by (e.g. 'python,react')"),
    min_attention_score: Optional[float] = Query(None, ge=0, description="Minimum attention score"),
    db: Session = Depends(get_db),
):
    """
    Fetch all enriched jobs with pagination and optional filters.
    - **source**: Filter by job source
    - **skills**: Comma-separated list of skills (matches jobs containing ALL listed skills)
    - **min_attention_score**: Minimum attention score threshold
    """
    # Parse skills string into a list
    skills_list = None
    if skills:
        skills_list = [s.strip() for s in skills.split(",") if s.strip()]

    skip = (page - 1) * per_page
    jobs, total = get_jobs(
        db,
        skip=skip,
        limit=per_page,
        source=source,
        skills=skills_list,
        min_attention_score=min_attention_score,
    )

    return JobListResponse(
        jobs=[JobResponse.from_db_model(j) for j in jobs],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get job details",
)
def get_job(job_id: str, db: Session = Depends(get_db)):
    """Fetch details for a specific job by its ID."""
    job = get_job_by_id(db, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id '{job_id}' not found",
        )
    return JobResponse.from_db_model(job)


@router.post(
    "/trigger-pipeline",
    response_model=PipelineTriggerResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger the scraping/enrichment pipeline (Admin only)",
)
def trigger_pipeline(
    background_tasks: BackgroundTasks,
    admin=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Triggers the existing pipeline.py in a background task.
    After the pipeline completes, results are synced into the database.
    Requires admin privileges.
    """
    from backend.services.pipeline_runner import run_pipeline_and_sync
    from backend.db.engine import SessionLocal

    background_tasks.add_task(run_pipeline_and_sync, SessionLocal)

    return PipelineTriggerResponse(
        message="Pipeline triggered successfully. Jobs will be updated shortly.",
        status="accepted",
    )
