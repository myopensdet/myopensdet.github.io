# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""What each status code looks like from Python. Run: python status_codes.py"""

import requests

for code in [200, 201, 204, 400, 401, 403, 404, 500, 503]:
    response = requests.get(f"https://httpbin.org/status/{code}", timeout=15)
    print(response.status_code, f"{response.reason:<22}", "ok" if response.ok else "not ok")

# requests doesn't raise an error for 4xx or 5xx. Ask it to:
response = requests.get("https://httpbin.org/status/404", timeout=15)
try:
    response.raise_for_status()
except requests.HTTPError as error:
    print("HTTPError:", error)
