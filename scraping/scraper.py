from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import json
import time
import requests
from processing.schema import create_job
from logger.logger import logger # Assuming your logger is here

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

# ----------------------------
# STEP 1: GET RECENT JOB LINKS
# ----------------------------
def get_remoteok_job_links(max_days=1):
    links = []
    now = datetime.now(timezone.utc)
    cutoff_date = now - timedelta(days=max_days)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=HEADERS["User-Agent"])

        try:
            page.goto("https://remoteok.com", wait_until="networkidle", timeout=60000)
            page.mouse.wheel(0, 2000)
            time.sleep(3)

            html_content = page.content()
            soup = BeautifulSoup(html_content, "html.parser")

            for row in soup.find_all("tr", class_="job"):
                # 1. Skip rows that aren't actual job listings
                if "job" not in row.get("class", []):
                    continue

                time_tag = row.find("time")
                if not time_tag or not time_tag.get("datetime"):
                    continue 

                # 2. Parse date safely
                date_str = time_tag["datetime"].replace("Z", "+00:00")
                job_datetime = datetime.fromisoformat(date_str)

                # 3. Check Date
                if job_datetime < cutoff_date:
                    # Check if this is a 'sticky' job (they are often old)
                    # We only break if it's a regular job that is old
                    if "sticky" in row.get("class", []):
                        logger.info(f"Skipping old sticky job: {row.get('data-slug')}")
                        continue 
                    else:
                        logger.info(f"Reached old regular job ({job_datetime.date()}). Stopping.")
                        break 

                job_path = row.get("data-href")
                if job_path:
                    links.append(f"https://remoteok.com{job_path}")
                    logger.info(f"Accepted: {row.get('data-slug')}")

        finally:
            browser.close()

    return links

# ----------------------------
# STEP 2: SCRAPE JOB DETAILS
# ----------------------------
def scrape_remoteok_job(job_url: str) -> dict:
    response = requests.get(job_url, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "Unknown"

    company_tag = soup.find("h3", attrs={"itemprop": "name"})
    company = company_tag.get_text(strip=True) if company_tag else "Unknown"

    skill_tags = soup.find_all("div", class_="tag")
    skills = [tag.find("h3").get_text(strip=True) for tag in skill_tags if tag.find("h3")]

    apply_input = soup.find("input", class_="share-job-copy-paste")
    apply_link = apply_input["value"] if apply_input else job_url

    job_id = job_url.rstrip("/").split("-")[-1]

    

    return create_job(
        job_id=f"remoteok-{job_id}",
        title=title,
        company=company,
        skills=skills,
        apply_link=apply_link,
        source="remoteok",
    )

# ----------------------------
# STEP 3: RUNNER
# ----------------------------
def scrape_all_remoteok_jobs():
    # We don't need a numeric limit here anymore because the date is our limit
    links = get_remoteok_job_links(max_days=1)
    jobs = []

    for url in links:
        try:
            job = scrape_remoteok_job(url)
            jobs.append(job)
            time.sleep(1) # Be polite
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")

    return jobs

if __name__ == "__main__":
    final_data = scrape_all_remoteok_jobs()
    
    with open("data/raw_jobs.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2)

    print(f"Extraction complete. {len(final_data)} recent jobs saved.")