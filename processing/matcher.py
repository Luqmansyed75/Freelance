import json
import argparse
from typing import List, Dict


def compute_attention_score(job: Dict, keywords: List[str]) -> float:
    title = job.get('title', '').lower()
    ai_summary = job.get('ai_summary', '').lower() if job.get('ai_summary') else ''
    description_items = [str(d).lower() for d in job.get('description', [])]
    job_skills = [str(s).lower() for s in job.get('skills', [])]

    score = 0.0
    matched_keywords = []

    # Weights (tunable)
    SKILL_W = 4.0
    TITLE_W = 3.0
    SUMMARY_W = 2.0
    DESC_W = 1.0

    for kw in keywords:
        k = kw.lower().strip()
        if not k:
            continue
        hit = False
        # Check extracted skills (highest weight — exact match)
        if k in job_skills:
            score += SKILL_W
            hit = True
        if k in title:
            score += TITLE_W
            hit = True
        if k in ai_summary:
            score += SUMMARY_W
            hit = True
        # count presence across description items
        for item in description_items:
            if k in item:
                score += DESC_W
                hit = True
        if hit:
            matched_keywords.append(k)

    return score, matched_keywords


def match_jobs_from_list(jobs: List[Dict], keywords: List[str], top_n: int = None, source_filter: str = None) -> List[Dict]:
    """Match jobs from an in-memory list (for Streamlit UI)."""
    results = []
    for job in jobs:
        # Apply source filter
        if source_filter and source_filter != "All":
            if job.get('source', '') != source_filter:
                continue

        score, matched_kw = compute_attention_score(job, keywords)
        if score > 0:
            job_copy = dict(job)
            job_copy['attention_score'] = score
            job_copy['matched_keywords'] = matched_kw
            results.append(job_copy)

    results.sort(key=lambda j: j.get('attention_score', 0), reverse=True)

    if top_n:
        results = results[:top_n]

    return results


def match_jobs(input_file: str, keywords: List[str], top_n: int = None, output_file: str = None) -> List[Dict]:
    with open(input_file, 'r', encoding='utf-8') as f:
        jobs = json.load(f)

    results = []
    for job in jobs:
        score, matched_kw = compute_attention_score(job, keywords)
        if score > 0:
            job_copy = dict(job)
            job_copy['attention_score'] = score
            job_copy['matched_keywords'] = matched_kw
            results.append(job_copy)

    # sort descending by attention_score
    results.sort(key=lambda j: j.get('attention_score', 0), reverse=True)

    if top_n:
        results = results[:top_n]

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)

    return results


def _parse_args():
    p = argparse.ArgumentParser(description='Match jobs by keywords and rank by attention score')
    p.add_argument('input_file', help='Enriched jobs JSON file')
    p.add_argument('keywords', nargs='+', help='Keywords to match (one or more)')
    p.add_argument('--top', type=int, default=None, help='Return top N results')
    p.add_argument('--out', default=None, help='Optional output JSON file to write results')
    return p.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    matched = match_jobs(args.input_file, args.keywords, top_n=args.top, output_file=args.out)
    for i, job in enumerate(matched, 1):
        print(f"{i}. [{job['attention_score']}] {job.get('title')} @ {job.get('company')}")