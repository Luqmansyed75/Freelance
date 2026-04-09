"""
CRUD operations for Application CRM model.
"""
from typing import Optional, List

from sqlalchemy.orm import Session, joinedload

from backend.models.application import Application
from backend.schemas.application import ApplicationCreate, ApplicationUpdate


def get_user_applications(db: Session, user_id: int) -> List[Application]:
    """Fetch all applications for a given user, with job details eager-loaded."""
    return (
        db.query(Application)
        .filter(Application.user_id == user_id)
        .options(joinedload(Application.job))
        .order_by(Application.created_at.desc())
        .all()
    )


def get_application_by_id(
    db: Session, app_id: int, user_id: int
) -> Optional[Application]:
    """Fetch a specific application belonging to a user."""
    return (
        db.query(Application)
        .filter(Application.id == app_id, Application.user_id == user_id)
        .options(joinedload(Application.job))
        .first()
    )


def create_application(
    db: Session, user_id: int, app_in: ApplicationCreate
) -> Application:
    """Save a job to the user's CRM."""
    application = Application(
        user_id=user_id,
        job_id=app_in.job_id,
        status=app_in.status,
        notes=app_in.notes,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def update_application(
    db: Session, app_id: int, user_id: int, app_update: ApplicationUpdate
) -> Optional[Application]:
    """Update an existing application's status, notes, or applied_date."""
    application = get_application_by_id(db, app_id, user_id)
    if not application:
        return None

    update_data = app_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)
    return application


def delete_application(db: Session, app_id: int, user_id: int) -> bool:
    """Delete an application from the user's CRM. Returns True if deleted."""
    application = get_application_by_id(db, app_id, user_id)
    if not application:
        return False
    db.delete(application)
    db.commit()
    return True
