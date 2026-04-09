"""
Skill Extraction Module (NLP — keyword-based + role inference)
Extracts relevant tech skills from job title and description tags using:
  1. A curated skill keyword set (~120 skills)
  2. Role-based inference (e.g., "Data Engineer" → data engineering)
Fast, free, and requires no AI API calls.
"""
import json
import re
from typing import List, Dict, Set


# Curated set of tech skills
TECH_SKILLS: Set[str] = {
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab",
    "perl", "shell", "bash", "sql", "html", "css",

    # Frontend
    "react", "reactjs", "react.js", "angular", "vue", "vuejs", "vue.js",
    "next.js", "nextjs", "nuxt", "svelte", "tailwind", "tailwindcss",
    "bootstrap", "sass", "webpack", "vite",

    # Backend
    "node.js", "nodejs", "express", "nest.js", "nestjs",
    "django", "flask", "fastapi",
    "spring", "spring boot", "rails", "laravel", ".net", "asp.net",
    "graphql", "rest", "restful", "api",

    # Data & ML
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn",
    "pandas", "numpy", "spark", "hadoop", "data science", "data engineering",
    "data analysis", "etl", "power bi", "tableau", "excel",
    "llm", "generative ai", "langchain", "rag",

    # Databases
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
    "sqlite", "dynamodb", "cassandra", "oracle", "sql server",
    "firebase", "supabase",

    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
    "terraform", "ansible", "jenkins", "ci/cd", "github actions",
    "linux", "nginx", "apache",

    # Tools & Misc
    "git", "github", "gitlab", "jira", "confluence", "figma",
    "agile", "scrum", "kanban",
    "blockchain", "web3", "solidity", "ethereum",
    "ios", "android", "react native", "flutter",
    "unity", "unreal",
    "cybersecurity", "security", "penetration testing",
    "seo", "wordpress", "shopify", "salesforce",
    "streamlit", "copilot",
}

# Role keywords in titles that imply specific skills
ROLE_SKILL_MAP = {
    "data engineer":       ["data engineering", "sql", "etl"],
    "data scientist":      ["data science", "python", "machine learning"],
    "data analyst":        ["data analysis", "sql", "excel"],
    "ml engineer":         ["machine learning", "python"],
    "machine learning":    ["machine learning"],
    "deep learning":       ["deep learning", "machine learning"],
    "devops":              ["docker", "ci/cd", "linux"],
    "frontend":            ["html", "css", "javascript"],
    "fullstack":           ["html", "css", "javascript"],
    "full stack":          ["html", "css", "javascript"],
    "backend":             ["api"],
    "ios developer":       ["ios", "swift"],
    "android developer":   ["android", "kotlin"],
    "mobile developer":    ["ios", "android"],
    "blockchain":          ["blockchain", "web3"],
    "cloud engineer":      ["aws", "docker"],
    "platform engineer":   ["docker", "kubernetes", "linux"],
    "security engineer":   ["security", "cybersecurity"],
    "qa engineer":         ["agile"],
    "quality engineer":    ["agile"],
    "sre":                 ["linux", "docker", "kubernetes"],
}


def extract_skills(description_tags: List[str], title: str = "") -> List[str]:
    """
    Extract tech skills from job description tags and title.
    Returns a sorted list of matched skills.
    """
    found_skills: Set[str] = set()

    # Combine title + description for keyword matching
    all_text = [title.lower()] + [str(tag).lower() for tag in description_tags]

    for text in all_text:
        for skill in TECH_SKILLS:
            # Use word boundary matching for short skills to avoid false positives
            if len(skill) <= 2:
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text):
                    found_skills.add(skill)
            else:
                if skill in text:
                    found_skills.add(skill)

    # Role-based inference from title
    title_lower = title.lower()
    for role_keyword, implied_skills in ROLE_SKILL_MAP.items():
        if role_keyword in title_lower:
            found_skills.update(implied_skills)

    # Normalize: if we matched "github" remove false-positive "git"
    # (git is a substring of github, only keep git if it matched independently)
    if "github" in found_skills and "git" in found_skills:
        # Check if "git" appears independently (not just inside "github")
        git_independent = False
        for text in all_text:
            # Match "git" as standalone word, not part of "github"/"gitlab"
            if re.search(r'\bgit\b(?!hub|lab)', text):
                git_independent = True
                break
        if not git_independent:
            found_skills.discard("git")

    return sorted(found_skills)


def enrich_jobs_with_skills(jobs: List[Dict]) -> List[Dict]:
    """Add a 'skills' field to each job based on extracted skills."""
    for job in jobs:
        skills = extract_skills(
            job.get('description', []),
            job.get('title', '')
        )
        job['skills'] = skills

    skills_found = sum(1 for j in jobs if j.get('skills'))
    print(f"Skill Extractor: {skills_found}/{len(jobs)} jobs have extracted skills.")
    return jobs


if __name__ == "__main__":
    input_file = "data/enriched_jobs.json"
    output_file = "data/final_jobs.json"

    with open(input_file, 'r', encoding='utf-8') as f:
        jobs = json.load(f)

    result = enrich_jobs_with_skills(jobs)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4)

    print(f"Saved {len(result)} jobs with skills to {output_file}")
