"""
Pydantic schemas for job data.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class SalaryResponse(BaseModel):
    """Nested salary information."""
    min: Optional[float] = None
    max: Optional[float] = None
    currency: str = "USD"


class JobResponse(BaseModel):
    """Schema for a single job returned to clients."""
    id: str
    title: str
    company: str
    source: str
    apply_link: Optional[str] = None
    description: Optional[List[str]] = []
    salary: SalaryResponse = SalaryResponse()
    ai_summary: Optional[str] = None
    skills: Optional[List[str]] = []
    scraped_at: Optional[datetime] = None
    attention_score: Optional[float] = 0.0

    model_config = {"from_attributes": True}

    @classmethod
    def from_db_model(cls, job) -> "JobResponse":
        """Convert a Job SQLAlchemy model to this response schema."""
        return cls(
            id=job.id,
            title=job.title,
            company=job.company,
            source=job.source,
            apply_link=job.apply_link,
            description=job.description or [],
            salary=SalaryResponse(
                min=job.salary_min,
                max=job.salary_max,
                currency=job.salary_currency or "USD",
            ),
            ai_summary=job.ai_summary,
            skills=job.skills or [],
            scraped_at=job.scraped_at,
            attention_score=job.attention_score,
        )


class JobListResponse(BaseModel):
    """Paginated list of jobs."""
    jobs: List[JobResponse]
    total: int
    page: int
    per_page: int


class PipelineTriggerResponse(BaseModel):
    """Response for pipeline trigger endpoint."""
    message: str
    status: str = "accepted"
