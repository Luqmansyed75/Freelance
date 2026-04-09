"""
Job model — stores enriched job data from the pipeline.
"""
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, Text, DateTime, JSON

from backend.db.engine import Base


class Job(Base):
    __tablename__ = "jobs"

    # PK is the hash ID from the pipeline, e.g. "nomads-429843898160288882"
    id = Column(String(255), primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    company = Column(String(500), nullable=False)
    source = Column(String(100), nullable=False, index=True)
    apply_link = Column(String(1000), nullable=True)

    # Description is stored as a JSON list of tag strings
    description = Column(JSON, nullable=True)

    # Salary fields (flattened from the nested salary dict)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), default="USD")

    # AI-generated summary
    ai_summary = Column(Text, nullable=True)

    # Extracted skills as a JSON list
    skills = Column(JSON, nullable=True)

    # Timestamps
    scraped_at = Column(DateTime, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Attention score (computed during matching, stored for sorting)
    attention_score = Column(Float, default=0.0, nullable=True)

    def __repr__(self):
        return f"<Job(id='{self.id}', title='{self.title}')>"
