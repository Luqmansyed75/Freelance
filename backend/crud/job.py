"""
CRUD operations for Job model.
"""
import json
import os
from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from backend.models.job import Job


def get_jobs(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    source: Optional[str] = None,
    skills: Optional[List[str]] = None,
    min_attention_score: Optional[float] = None,
) -> tuple[list[Job], int]:
    """
    Fetch jobs with pagination and optional filters.
    Returns (list_of_jobs, total_count).
    """
    query = db.query(Job)

    # Filter by source
    if source:
        query = query.filter(Job.source == source)

    # Filter by minimum attention score
    if min_attention_score is not None:
        query = query.filter(Job.attention_score >= min_attention_score)

    # Filter by skills (jobs that contain ANY of the specified skills)
    if skills:
        from sqlalchemy import String
        for skill in skills:
            skill_lower = skill.strip().lower()
            # JSON column contains check — works with SQLite JSON1 extension
            query = query.filter(
                Job.skills.cast(String).ilike(f"%{skill_lower}%")
            )

    total = query.count()
    jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

    return jobs, total


def get_job_by_id(db: Session, job_id: str) -> Optional[Job]:
    """Fetch a single job by its ID."""
    return db.query(Job).filter(Job.id == job_id).first()


def upsert_jobs_from_json(db: Session, json_path: str) -> int:
    """
    Read final_jobs.json and upsert all jobs into the database.
    Uses raw SQL INSERT OR REPLACE for reliable SQLite upserts.
    Returns the number of jobs upserted.
    """
    if not os.path.exists(json_path):
        return 0

    with open(json_path, "r", encoding="utf-8") as f:
        jobs_data = json.load(f)

    from sqlalchemy import text
    from datetime import datetime as dt, timezone

    sql = text("""
        INSERT OR REPLACE INTO jobs
            (id, title, company, source, apply_link, description,
             salary_min, salary_max, salary_currency, ai_summary,
             skills, scraped_at, created_at, attention_score)
        VALUES
            (:id, :title, :company, :source, :apply_link, :description,
             :salary_min, :salary_max, :salary_currency, :ai_summary,
             :skills, :scraped_at, :created_at, :attention_score)
    """)

    count = 0
    now = dt.now(timezone.utc).isoformat()

    for job_dict in jobs_data:
        job_id = job_dict.get("id")
        if not job_id:
            continue

        # Parse scraped_at
        scraped_at = None
        if job_dict.get("scraped_at"):
            try:
                scraped_at = job_dict["scraped_at"]
            except (ValueError, TypeError):
                scraped_at = None

        # Extract salary
        salary = job_dict.get("salary", {})

        db.execute(sql, {
            "id": job_id,
            "title": job_dict.get("title", "Unknown"),
            "company": job_dict.get("company", "Unknown"),
            "source": job_dict.get("source", "unknown"),
            "apply_link": job_dict.get("apply_link"),
            "description": json.dumps(job_dict.get("description", [])),
            "salary_min": salary.get("min"),
            "salary_max": salary.get("max"),
            "salary_currency": salary.get("currency", "USD"),
            "ai_summary": job_dict.get("ai_summary"),
            "skills": json.dumps(job_dict.get("skills", [])),
            "scraped_at": scraped_at,
            "created_at": now,
            "attention_score": job_dict.get("attention_score", 0.0),
        })
        count += 1

    db.commit()
    return count

