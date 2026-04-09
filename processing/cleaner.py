"""
Data Cleaning & Filtering Module
Cleans raw scraped job data: removes empty/spam entries, normalizes text.
"""
import json
import re
from typing import List, Dict


# Words that indicate spam or irrelevant listings
SPAM_INDICATORS = [
    "click here", "subscribe", "sign up", "advertisement",
    "buy now", "limited offer", "act now", "earn money fast",
]


def clean_description(tags: List[str]) -> List[str]:
    """Remove empty strings, normalize whitespace and casing."""
    cleaned = []
    for tag in tags:
        tag = tag.strip()
        if not tag:
            continue
        # Normalize whitespace (collapse multiple spaces)
        tag = re.sub(r'\s+', ' ', tag)
        # Lowercase for consistency
        tag = tag.lower()
        cleaned.append(tag)
    # Remove exact duplicates while preserving order
    seen = set()
    unique = []
    for t in cleaned:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique


def is_valid_job(job: Dict) -> bool:
    """Filter out jobs with missing critical fields or spam indicators."""
    title = job.get('title', '').strip()
    company = job.get('company', '').strip()

    # Must have a title and company
    if not title or title.lower() in ('n/a', 'unknown', ''):
        return False
    if not company or company.lower() in ('n/a', 'unknown', ''):
        return False

    # Check for spam in title or description
    combined_text = title.lower()
    for tag in job.get('description', []):
        combined_text += ' ' + str(tag).lower()

    for spam_word in SPAM_INDICATORS:
        if spam_word in combined_text:
            return False

    return True


def clean_jobs(jobs: List[Dict]) -> List[Dict]:
    """Apply cleaning and filtering to a list of jobs."""
    cleaned = []
    removed_count = 0

    for job in jobs:
        # 1. Validate the job
        if not is_valid_job(job):
            removed_count += 1
            continue

        # 2. Clean description tags
        job['description'] = clean_description(job.get('description', []))

        # 3. Normalize title and company
        job['title'] = job['title'].strip()
        job['company'] = job['company'].strip()

        cleaned.append(job)

    print(f"Cleaner: {len(cleaned)} valid jobs kept, {removed_count} removed.")
    return cleaned


if __name__ == "__main__":
    input_file = "data/nomad.json"
    output_file = "data/clean_jobs.json"

    with open(input_file, 'r', encoding='utf-8') as f:
        raw_jobs = json.load(f)

    result = clean_jobs(raw_jobs)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4)

    print(f"Saved {len(result)} clean jobs to {output_file}")
