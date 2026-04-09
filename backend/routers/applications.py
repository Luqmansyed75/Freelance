"""
Applications CRM router — save, list, update, and delete job applications.
All endpoints require JWT authentication.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.db.deps import get_db
from backend.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
)
from backend.crud.application import (
    get_user_applications,
    get_application_by_id,
    create_application,
    update_application,
    delete_application,
)
from backend.crud.job import get_job_by_id
from backend.core.security import get_current_user

router = APIRouter(prefix="/applications", tags=["Applications CRM"])


@router.get(
    "",
    response_model=List[ApplicationResponse],
    summary="List my applications",
)
def list_applications(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all saved/applied jobs for the currently authenticated user."""
    apps = get_user_applications(db, user_id=current_user.id)
    return [ApplicationResponse.from_db_model(a) for a in apps]


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a job to CRM",
)
def save_application(
    app_in: ApplicationCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Save a job to the authenticated user's CRM.
    Returns 404 if the job doesn't exist, 409 if already saved.
    """
    # Verify the job exists
    job = get_job_by_id(db, job_id=app_in.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id '{app_in.job_id}' not found",
        )

    try:
        application = create_application(db, user_id=current_user.id, app_in=app_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already saved this job",
        )

    # Re-fetch with job relationship loaded
    application = get_application_by_id(db, app_id=application.id, user_id=current_user.id)
    return ApplicationResponse.from_db_model(application)


@router.patch(
    "/{app_id}",
    response_model=ApplicationResponse,
    summary="Update an application",
)
def update_app(
    app_id: int,
    app_update: ApplicationUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the status, notes, or applied_date of an application."""
    application = update_application(
        db, app_id=app_id, user_id=current_user.id, app_update=app_update
    )
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id {app_id} not found",
        )
    return ApplicationResponse.from_db_model(application)


@router.delete(
    "/{app_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an application",
)
def delete_app(
    app_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a job from the user's CRM."""
    deleted = delete_application(db, app_id=app_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id {app_id} not found",
        )
    return None
