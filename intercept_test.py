from playwright.sync_api import sync_playwright
import json

def test_intercept():
    api_responses = []
    
    def handle_response(response):
        if "api" in response.url or "_search" in response.url or "workingnomads" in response.url:
            if response.request.resource_type in ["xhr", "fetch"]:
                try:
                    body = response.json()
                    api_responses.append({"url": response.url, "body": body})
                except Exception:
                    pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = context.new_page()
        page.on("response", handle_response)
        page.goto("https://www.workingnomads.com/jobs?positionType=contract")
        page.wait_for_timeout(5000)
        
        print(f"Captured {len(api_responses)} JSON responses.")
        for r in api_responses:
            # Look for payloads that likely contain jobs
            dump = json.dumps(r["body"])
            if "title" in dump:
                print("Found possible Job API:", r["url"])
                print("Sample:", dump[:1000])
                break
        else:
            print("No job-like API response found.")
        browser.close()

if __name__ == "__main__":
    test_intercept()
