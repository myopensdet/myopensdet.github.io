# Template from myOpenSDET: https://myopensdet.github.io/
"""How HTTP works: one request, and everything in the answer. Run: python http_basics.py"""

import requests

response = requests.get("https://httpbin.org/get", params={"page": 2}, timeout=15)

print("Request: ", response.request.method, response.request.url)
print("Status:  ", response.status_code, response.reason)
print("Type:    ", response.headers["Content-Type"])
print("OK?      ", response.ok)
body = response.json()
print("Body has:", sorted(body))
print("args:    ", body["args"])
