# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Check a real response against a JSON Schema, then a broken copy. Run: python schema_demo.py

Needs BOOKER_USERNAME and BOOKER_PASSWORD, to delete the booking it makes.
"""

import os
import sys
from pathlib import Path

import requests

# Use the schema helper from this topic's template project.
sys.path.insert(0, str(Path(__file__).parents[1] / "templates" / "booker_api_tests"))
from api.schema import load_schema, schema_errors  # noqa: E402

BASE = "https://restful-booker.herokuapp.com"
JSON = {"Accept": "application/json"}
schema = load_schema("booking.json")

# Create our own booking, so nobody else's data can change the result.
new = {
    "firstname": "Test",
    "lastname": "Booker",
    "totalprice": 120,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-12-01", "checkout": "2026-12-03"},
}
booking_id = requests.post(f"{BASE}/booking", json=new, headers=JSON, timeout=15).json()[
    "bookingid"
]
booking = requests.get(f"{BASE}/booking/{booking_id}", headers=JSON, timeout=15).json()
print("Real booking:", schema_errors(booking, schema) or "matches the schema")

broken = {
    **booking,
    "totalprice": "120",
    "bookingdates": {"checkin": "2026-13-01"},
    "discount": 10,
}
print("Broken copy:")
for problem in schema_errors(broken, schema):
    print("-", problem)

# Clean up: delete the booking we made (needs Restful-booker's public demo login).
login = {"username": os.environ["BOOKER_USERNAME"], "password": os.environ["BOOKER_PASSWORD"]}
token = requests.post(f"{BASE}/auth", json=login, timeout=15).json()["token"]
requests.delete(f"{BASE}/booking/{booking_id}", headers={"Cookie": f"token={token}"}, timeout=15)
