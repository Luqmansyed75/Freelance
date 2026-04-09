from datetime import datetime
from typing import List, Dict, Optional


def create_job(
    job_id: str,
    title: str,
    company: str,
    description: List[str],
    apply_link: str,
    source: str,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    currency: Optional[str] = None,
) -> Dict:
    """Create a standardized job dict used by all scrapers."""
    job = {
        "id": job_id,
        "title": title.strip(),
        "company": company.strip(),
        "description": list(set(desc.lower() for desc in description)),
        "salary": {
            "min": salary_min,
            "max": salary_max,
            "currency": currency,
        },
        "apply_link": apply_link,
        "source": source.lower(),
        "scraped_at": datetime.utcnow().isoformat(),
    }
    return job
