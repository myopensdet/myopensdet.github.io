# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Query parameters and path parameters. Run: python params.py"""

import requests

response = requests.get(
    "https://httpbin.org/get", params={"q": "বই", "sort": "price", "page": 2}, timeout=15
)
print("URL sent:", response.url)
print("Server read:", response.json()["args"])

# A path parameter is part of the path: /booking/<id>.
# Ask for one that exists, and one that doesn't.
BASE = "https://restful-booker.herokuapp.com"
JSON = {"Accept": "application/json"}
existing = requests.get(f"{BASE}/booking", timeout=15).json()[0]["bookingid"]
for booking_id in [existing, 999999999]:
    response = requests.get(f"{BASE}/booking/{booking_id}", headers=JSON, timeout=15)
    print(
        "/booking/<id>:",
        "an id from the list" if booking_id == existing else booking_id,
        "->",
        response.status_code,
    )
