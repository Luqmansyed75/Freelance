"""
Pydantic schemas for the Application CRM.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from backend.schemas.job import JobResponse


class ApplicationCreate(BaseModel):
    """Schema for saving a job to the user's CRM."""
    job_id: str
    status: str = Field(default="Saved", pattern="^(Saved|Applied|Interviewing|Rejected|Accepted)$")
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    """Schema for updating an application entry."""
    status: Optional[str] = Field(default=None, pattern="^(Saved|Applied|Interviewing|Rejected|Accepted)$")
    notes: Optional[str] = None
    applied_date: Optional[datetime] = None


class ApplicationResponse(BaseModel):
    """Schema for a single application returned to clients."""
    id: int
    user_id: int
    job_id: str
    status: str
    notes: Optional[str] = None
    applied_date: Optional[datetime] = None
    created_at: datetime

    # Nested job details
    job: Optional[JobResponse] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_db_model(cls, app) -> "ApplicationResponse":
        """Convert an Application SQLAlchemy model to this response schema."""
        job_resp = None
        if app.job:
            job_resp = JobResponse.from_db_model(app.job)
        return cls(
            id=app.id,
            user_id=app.user_id,
            job_id=app.job_id,
            status=app.status,
            notes=app.notes,
            applied_date=app.applied_date,
            created_at=app.created_at,
            job=job_resp,
        )
