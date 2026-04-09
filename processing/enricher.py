"""
Data Enrichment Module
Enriches jobs with salary extraction and AI summary placeholder.
No external API calls — runs fully offline.
"""
import json
import os
import re
from datetime import datetime
from typing import List, Dict


def extract_salary_from_list(desc_list):
    """Extracts numeric salary from strings like '$127k-$159k'."""
    salary_data = {"min": None, "max": None, "currency": "USD"}
    pattern = r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?k?)'

    for item in desc_list:
        if '$' in item:
            matches = re.findall(pattern, item)
            if matches:
                nums = []
                for m in matches:
                    val = m.replace(',', '').lower()
                    num = float(val.replace('k', '')) * 1000 if 'k' in val else float(val)
                    nums.append(num)
                if len(nums) >= 2:
                    salary_data["min"], salary_data["max"] = min(nums), max(nums)
                elif len(nums) == 1:
                    salary_data["min"] = nums[0]
            return salary_data, item
    return salary_data, None


def _generate_summary(title: str, company: str, tags: List[str]) -> str:
    """Generate a simple offline summary from title, company and tags."""
    clean_tags = [t for t in tags if t.strip()]
    if clean_tags:
        return f"{title} at {company}. Tags: {', '.join(clean_tags)}."
    return f"{title} at {company}."


def _load_existing_enriched(output_file: str) -> dict:
    """Load already-enriched jobs into a lookup dict by job ID."""
    if not os.path.exists(output_file):
        return {}
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        return {job['id']: job for job in existing if job.get('id')}
    except (json.JSONDecodeError, KeyError):
        return {}


def _has_valid_summary(job: dict) -> bool:
    """Check if a job already has a valid AI summary."""
    summary = job.get('ai_summary', '')
    return summary and summary != "Summary unavailable."


def enrich_job_data(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        jobs = json.load(f)

    # Load existing enriched data to skip already-processed jobs
    existing_enriched = _load_existing_enriched(output_file)

    enriched_list = []
    new_enrichments = 0
    skipped = 0

    for job in jobs:
        # 1. Check if already enriched with valid summary
        job_id = job.get('id', '')
        if job_id in existing_enriched and _has_valid_summary(existing_enriched[job_id]):
            enriched_list.append(existing_enriched[job_id])
            skipped += 1
            continue

        # 2. Extract Salary
        desc = job.get('description', [])
        salary_info, raw_salary_str = extract_salary_from_list(desc)
        job['salary'] = {"min": salary_info["min"], "max": salary_info["max"], "currency": salary_info["currency"]}

        # 3. Generate offline summary (no API call)
        tags_str_list = [t for t in desc if t != raw_salary_str and t != ""]
        job['ai_summary'] = _generate_summary(job['title'], job['company'], tags_str_list)
        job['description'] = tags_str_list if tags_str_list else desc
        new_enrichments += 1

        enriched_list.append(job)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched_list, f, indent=4)
    print(f"Enricher: {len(enriched_list)} jobs saved ({new_enrichments} new, {skipped} reused from cache)")


if __name__ == "__main__":
    enrich_job_data('data/deduped_jobs.json', 'data/enriched_jobs.json')