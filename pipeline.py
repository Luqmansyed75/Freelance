"""
Pipeline Runner
Runs the full job processing pipeline in order:
  1. Clean raw jobs
  2. Deduplicate
  3. Enrich (AI summaries + salary — skips already-enriched)
  4. Extract skills
"""
import json
import os
import sys

from processing.cleaner import clean_jobs
from processing.deduplicator import deduplicate_jobs
from processing.enricher import enrich_job_data
from processing.skill_extractor import enrich_jobs_with_skills


# File paths
RAW_FILES = ["data/nomad.json", "data/wwr.json"]
CLEAN_FILE = "data/clean_jobs.json"
DEDUPED_FILE = "data/deduped_jobs.json"
ENRICHED_FILE = "data/enriched_jobs.json"
FINAL_FILE = "data/final_jobs.json"


def run_pipeline():
    print("=" * 50)
    print("  FREELANCE JOB PIPELINE")
    print("=" * 50)

    # Load and merge all raw sources
    raw_jobs = []
    for raw_file in RAW_FILES:
        if os.path.exists(raw_file):
            with open(raw_file, 'r', encoding='utf-8') as f:
                jobs = json.load(f)
            print(f"Loaded {len(jobs)} jobs from {raw_file}")
            raw_jobs.extend(jobs)
        else:
            print(f"Warning: '{raw_file}' not found, skipping.")

    if not raw_jobs:
        print("Error: No raw job files found. Run a scraper first.")
        sys.exit(1)

    print(f"Total raw jobs from all sources: {len(raw_jobs)}")

    # Step 1: Clean
    print("\n--- Step 1: Cleaning ---")
    cleaned = clean_jobs(raw_jobs)
    with open(CLEAN_FILE, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, indent=4)

    # Step 2: Deduplicate
    print("\n--- Step 2: Deduplicating ---")
    deduped = deduplicate_jobs(cleaned)
    with open(DEDUPED_FILE, 'w', encoding='utf-8') as f:
        json.dump(deduped, f, indent=4)

    # Step 3: Enrich (AI summaries + salary)
    print("\n--- Step 3: Enriching (AI + Salary) ---")
    enrich_job_data(DEDUPED_FILE, ENRICHED_FILE)

    # Step 4: Extract Skills
    print("\n--- Step 4: Extracting Skills ---")
    with open(ENRICHED_FILE, 'r', encoding='utf-8') as f:
        enriched = json.load(f)
    final = enrich_jobs_with_skills(enriched)
    with open(FINAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(final, f, indent=4)

    print("\n" + "=" * 50)
    print(f"  PIPELINE COMPLETE: {len(final)} jobs in {FINAL_FILE}")
    print("=" * 50)


if __name__ == "__main__":
    run_pipeline()
