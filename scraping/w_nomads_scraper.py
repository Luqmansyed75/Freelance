from playwright.sync_api import sync_playwright
import json
import time
from processing.schema import create_job
from logger.logger import logger

def get_nomads_jobs():
    url = "https://www.workingnomads.com/jobs?positionType=contract"
    jobs = []
    api_payloads = []

    with sync_playwright() as p:
        logger.info("Launching browser for Working Nomads API Interception...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        def handle_response(response):
            if "jobsapi" in response.url or "_search" in response.url:
                try:
                    data = response.json()
                    api_payloads.append(data)
                except Exception as e:
                    print("JSON error for", response.url, ":", e)

        try:
            page.on("response", handle_response)
            logger.info(f"Navigating to {url}...")
            # Wait for the main shell to load
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # TRIGGER LOADING: Scroll down and wait
            logger.info("Scrolling to trigger dynamic load...")
            page.mouse.wheel(0, 1500)
            page.wait_for_timeout(5000) # Give the JavaScript 5 seconds to fill the list and complete API requests
            
            for data in api_payloads:
                hits = data.get("hits", {}).get("hits", [])
                for hit in hits:
                    source = hit.get("_source", {})
                    title = source.get("title", "N/A")
                    company = source.get("company", "Unknown")
                    tags = source.get("tags", [])
                    
                    # The actual specific job applying link is the external URL or the workingnomads job page
                    apply_url = source.get("apply_url")
                    slug = source.get("slug")
                    job_id = source.get("id")
                    
                    # Prefer the direct apply URL, fallback to specific job page
                    if apply_url and apply_url.strip():
                        apply_link = apply_url
                    elif slug and job_id:
                        apply_link = f"https://www.workingnomads.com/jobs/{slug}-{job_id}"
                    else:
                        apply_link = url

                    # Create standardized job
                    job = create_job(
                        job_id=f"nomads-{hash(title + company)}",
                        title=title,
                        company=company,
                        description=tags,
                        apply_link=apply_link,
                        source="working_nomads"
                    )
                    jobs.append(job)

            # Deduplicate just in case the API returned duplicates or we intercepted multiple pages
            unique_jobs = {j["id"]: j for j in jobs}
            jobs = list(unique_jobs.values())

            logger.info(f"Scraped {len(jobs)} jobs from Working Nomads API interception.")

        except Exception as e:
            logger.error(f"Nomads Scraper Error: {e}")
        finally:
            browser.close()

    return jobs

if __name__ == "__main__":
    results = get_nomads_jobs()
    with open("data/nomad.json", "w") as f:
        json.dump(results, f, indent=4)
    print(f"Final Count: {len(results)} jobs found.")