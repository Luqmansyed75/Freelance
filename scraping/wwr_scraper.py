import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import re
from processing.schema import create_job
from logger.logger import logger

# Constants
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
}

def extract_salary_range(text):
    """Simple regex to pull salary numbers from a string if present."""
    if not text: return None, None
    # Matches patterns like $50,000, $100k, 50k
    matches = re.findall(r'\$?(\d{1,3}(?:,\d{3})*k?)', text.lower())
    try:
        if len(matches) >= 2:
            return matches[0], matches[1]
        elif len(matches) == 1:
            return matches[0], None
    except:
        pass
    return None, None

def get_wwr_jobs():
    url = "https://weworkremotely.com/remote-contract-jobs"
    jobs = []
    
    try:
        logger.info(f"Connecting to WWR Contract Board...")
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # WWR structure: Jobs are typically inside <li> tags within sections
        # We target the actual job rows to avoid ads/headers
        job_rows = soup.find_all('li', class_=lambda x: x != 'view-all')

        for row in job_rows:
            # 1. Title (using your confirmed selector)
            title_tag = row.find('h3', class_='new-listing__header__title') or row.find('span', class_='title')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)

            # 2. Company (using your confirmed selector)
            company_tag = row.find('p', class_='new-listing__company-name') or row.find('span', class_='company')
            company = company_tag.get_text(strip=True) if company_tag else "Unknown"

            # 3. Apply Link
            # The <a> tag usually wraps the entire row or the title
            link_tag = row.find('a', href=True)
            if not link_tag:
                continue
            apply_link = f"https://weworkremotely.com{link_tag['href']}"

            # 4. Tags / Description / Salary
            # WWR places metadata (Contract, region, salary) in div.new-listing__categories > p
            tags = []
            categories_div = row.find('div', class_='new-listing__categories')
            if categories_div:
                for p_tag in categories_div.find_all('p'):
                    text = p_tag.get_text(strip=True)
                    if text:
                        tags.append(text)

            # Also try the older span-based selectors as fallback
            if not tags:
                metadata = row.find_all('span', class_=lambda x: x in ['region', 'listing-metadata', 'contract'])
                for meta in metadata:
                    text = meta.get_text(strip=True)
                    if text:
                        tags.append(text)

            # Extract salary from tags
            salary_min, salary_max = None, None
            for tag_text in tags:
                if '$' in tag_text:
                    salary_min, salary_max = extract_salary_range(tag_text)
                    break

            # 5. Unique ID
            # WWR paths look like: /remote-jobs/company-job-title
            job_id_slug = link_tag['href'].split('/')[-1]

            # 6. Create standardized job using your schema
            job = create_job(
                job_id=f"wwr-{job_id_slug}",
                title=title,
                company=company,
                description=tags,
                apply_link=apply_link,
                source="wwr",
                salary_min=salary_min,
                salary_max=salary_max
            )
            jobs.append(job)
            
        logger.info(f"Scraped {len(jobs)} freelance jobs from WWR.")
        
    except Exception as e:
        logger.error(f"WWR Scraper failed: {e}")

    return jobs

if __name__ == "__main__":
    results = get_wwr_jobs()
    # Save the result to check the JSON structure
    with open("data/wwr.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Verified and saved {len(results)} jobs.")