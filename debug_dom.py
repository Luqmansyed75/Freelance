from playwright.sync_api import sync_playwright

def get_job_html():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )
        page = context.new_page()
        page.goto("https://www.workingnomads.com/jobs?positionType=contract")
        page.mouse.wheel(0, 1500)
        page.wait_for_timeout(5000)
        
        # Print the first job card outer HTML
        loc = page.locator(".job-wrapper").first
        if loc.count() == 0:
            loc = page.locator(".job").first
        
        print(loc.evaluate("el => el.outerHTML"))
        browser.close()

if __name__ == "__main__":
    get_job_html()
