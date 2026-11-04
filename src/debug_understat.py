import requests

HEADERS = {"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}

# 1) the league page the package scrapes
r = requests.get("https://understat.com/league/EPL/2026", headers=HEADERS, timeout=30)
print("PAGE:", r.status_code, "| has datesData:", "datesData" in r.text, "| length:", len(r.text))

# 2) a direct data endpoint some newer scrapers use (not certain it works)
r2 = requests.get("https://understat.com/getLeagueData/EPL/2026", headers=HEADERS, timeout=30)
print("API:", r2.status_code, "| first 200 chars:", r2.text[:200])