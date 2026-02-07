import requests
from bs4 import BeautifulSoup

URL = "https://remoteok.com/remote-jobs/remote-senior-automation-engineer-java-ubiminds-1130093"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=HEADERS)
soup = BeautifulSoup(response.text, "html.parser")


# ----------------------------
# TITLE
# ----------------------------
title_tag = soup.find("h1")
title = title_tag.get_text(strip=True) if title_tag else None


# ----------------------------
# COMPANY (RemoteOK uses h2 near title)
# ----------------------------
company_tag = soup.find("h2")
company = company_tag.get_text(strip=True) if company_tag else None


# ----------------------------
# DESCRIPTION
# ----------------------------
desc_div = soup.find("div", id="job_description")

if desc_div:
    description = desc_div.get_text(separator="\n", strip=True)
else:
    description = None


# ----------------------------
# SALARY (safe method)
# ----------------------------
salary = None

possible_salary = soup.find("div", class_="salary")

if possible_salary:
    salary = possible_salary.get_text(strip=True)


# ----------------------------
# OUTPUT
# ----------------------------
print("Title:", title)
print("Company:", company)
print("Salary:", salary)
print("Description:", description[:500] if description else None)
