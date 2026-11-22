# Template from myOpenSDET: https://myopensdet.github.io/
"""Headers, and the two ways to send data. Run: python headers_and_json.py"""

import requests

sent = requests.get(
    "https://httpbin.org/headers",
    headers={"Accept": "application/json", "X-Test-Run": "nightly-42"},
    timeout=15,
).json()["headers"]
print("The server saw:", {name: sent[name] for name in ["Accept", "X-Test-Run", "User-Agent"]})

reading = {"device_id": "SNS-0042", "location": "ঢাকা অফিস", "battery": 87}

as_json = requests.post("https://httpbin.org/anything", json=reading, timeout=15)
print("json=  ->", as_json.json()["headers"]["Content-Type"], as_json.json()["json"])

as_form = requests.post("https://httpbin.org/anything", data=reading, timeout=15)
print("data=  ->", as_form.json()["headers"]["Content-Type"], as_form.json()["form"])

response = requests.get("https://httpbin.org/json", timeout=15)
print("Response type:", response.headers["Content-Type"])
print("Title:", response.json()["slideshow"]["title"])
