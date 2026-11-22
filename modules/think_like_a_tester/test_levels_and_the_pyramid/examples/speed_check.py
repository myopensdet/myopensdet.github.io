# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""A first, tiny performance check: how fast does one endpoint answer, again and again?

This is not a load test (that comes later, with Locust or k6). It answers a
simpler question: is this endpoint fast on its own, and does it stay fast?

    python speed_check.py
"""

import statistics
import time

from fastapi.testclient import TestClient
from shop.api import app

REQUESTS = 200
LIMIT_MS = 50  # agree this number with your team; it is an example

client = TestClient(app)
order = {"lines": [{"name": "Python book", "price_cents": 2500, "quantity": 2}], "coupon": "SAVE10"}

timings = []
for _ in range(REQUESTS):
    start = time.perf_counter()
    response = client.post("/api/cart/totals", json=order)
    timings.append((time.perf_counter() - start) * 1000)
    assert response.status_code == 200

timings.sort()
p95 = timings[int(len(timings) * 0.95) - 1]
print(f"{REQUESTS} requests")
print(f"median: {statistics.median(timings):.1f} ms")
print(f"95th percentile: {p95:.1f} ms  (95 out of 100 requests were this fast or faster)")
print(f"slowest: {timings[-1]:.1f} ms")
print("OK" if p95 <= LIMIT_MS else f"TOO SLOW: the 95th percentile is over {LIMIT_MS} ms")
