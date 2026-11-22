# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""GET, POST, PUT, PATCH and DELETE on one booking. Run: python methods_tour.py

Needs BOOKER_USERNAME and BOOKER_PASSWORD (Restful-booker's public demo account).
"""

import os

import requests

BASE = "https://restful-booker.herokuapp.com"
JSON = {"Accept": "application/json"}

login = {"username": os.environ["BOOKER_USERNAME"], "password": os.environ["BOOKER_PASSWORD"]}
token = requests.post(f"{BASE}/auth", json=login, timeout=15).json()["token"]
auth = {**JSON, "Cookie": f"token={token}"}

booking = {
    "firstname": "Test",
    "lastname": "Booker",
    "totalprice": 120,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-12-01", "checkout": "2026-12-03"},
    "additionalneeds": "Breakfast",
}

created = requests.post(f"{BASE}/booking", json=booking, headers=JSON, timeout=15)
booking_id = created.json()["bookingid"]
print("POST   ", created.status_code, "new booking id:", booking_id)

read = requests.get(f"{BASE}/booking/{booking_id}", headers=JSON, timeout=15)
print("GET    ", read.status_code, read.json()["firstname"], read.json()["totalprice"])

replaced = requests.put(
    f"{BASE}/booking/{booking_id}", json={**booking, "totalprice": 150}, headers=auth, timeout=15
)
print("PUT    ", replaced.status_code, "totalprice is now", replaced.json()["totalprice"])

patched = requests.patch(
    f"{BASE}/booking/{booking_id}",
    json={"additionalneeds": "Late checkout"},
    headers=auth,
    timeout=15,
)
print(
    "PATCH  ", patched.status_code, patched.json()["additionalneeds"], patched.json()["totalprice"]
)

deleted = requests.delete(f"{BASE}/booking/{booking_id}", headers=auth, timeout=15)
print("DELETE ", deleted.status_code, deleted.text)

gone = requests.get(f"{BASE}/booking/{booking_id}", headers=JSON, timeout=15)
print("GET    ", gone.status_code, gone.text)
