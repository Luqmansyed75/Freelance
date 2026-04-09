"""
Application CRM model — tracks user's saved/applied jobs.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from backend.db.engine import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String(255), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)

    # Status: Saved, Applied, Interviewing, Rejected, Accepted
    status = Column(String(50), default="Saved", nullable=False)
    notes = Column(Text, nullable=True)
    applied_date = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # One user can only have one application per job
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job"),
    )

    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("Job")

    def __repr__(self):
        return f"<Application(id={self.id}, user_id={self.user_id}, job_id='{self.job_id}', status='{self.status}')>"
