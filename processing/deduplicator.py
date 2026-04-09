"""
Duplicate Detection Module
Removes duplicate job listings across scraping sources using title+company similarity.
Uses stdlib SequenceMatcher — no extra dependencies needed.
"""
import json
from difflib import SequenceMatcher
from typing import List, Dict


def normalize_text(text: str) -> str:
    """Lowercase, strip whitespace, remove special characters."""
    text = text.lower().strip()
    # Remove special chars but keep spaces
    text = ''.join(c for c in text if c.isalnum() or c.isspace())
    # Collapse multiple spaces
    return ' '.join(text.split())


def is_duplicate(job: Dict, existing_jobs: List[Dict], threshold: float = 0.85) -> bool:
    """
    Check if a job is a duplicate of any existing job.
    Compares normalized title+company using SequenceMatcher.
    """
    job_key = normalize_text(f"{job.get('title', '')} {job.get('company', '')}")

    for existing in existing_jobs:
        existing_key = normalize_text(f"{existing.get('title', '')} {existing.get('company', '')}")
        similarity = SequenceMatcher(None, job_key, existing_key).ratio()
        if similarity >= threshold:
            return True

    return False


def deduplicate_jobs(jobs: List[Dict], threshold: float = 0.85) -> List[Dict]:
    """Remove duplicate jobs from a list. Keeps the first occurrence."""
    unique_jobs = []
    duplicates_removed = 0

    for job in jobs:
        if not is_duplicate(job, unique_jobs, threshold):
            unique_jobs.append(job)
        else:
            duplicates_removed += 1

    print(f"Deduplicator: {len(unique_jobs)} unique jobs kept, {duplicates_removed} duplicates removed.")
    return unique_jobs


if __name__ == "__main__":
    input_file = "data/clean_jobs.json"
    output_file = "data/deduped_jobs.json"

    with open(input_file, 'r', encoding='utf-8') as f:
        jobs = json.load(f)

    result = deduplicate_jobs(jobs)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4)

    print(f"Saved {len(result)} deduplicated jobs to {output_file}")
