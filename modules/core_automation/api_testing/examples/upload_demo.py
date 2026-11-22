# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Upload a file, with a form field. Run: python upload_demo.py"""

from pathlib import Path

import requests

report = Path(__file__).parent / "results.csv"
with report.open("rb") as file:
    response = requests.post(
        "https://httpbin.org/post",
        files={"file": ("results.csv", file, "text/csv")},
        data={"run": "nightly"},
        timeout=15,
    )

body = response.json()
print("Status:", response.status_code)
print("Sent as:", body["headers"]["Content-Type"].split(";")[0])
print("Form field:", body["form"])
received = body["files"]["file"]
print(
    "File received:",
    len(received.splitlines()),
    "lines, the same as sent:",
    received == report.read_text(),
)
