# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Speed targets as tests: each page must answer fast enough, without errors,
while several users use it at once. Run them on a test environment, never production."""

import os

import pytest
from speed_check import report, run

# CHANGE 1: the address of the API you test.
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8770")
SECONDS = float(os.environ.get("SPEED_SECONDS", "5"))  # how long each check runs

# CHANGE 2: your pages and the targets your team agreed on.
TARGETS = [
    # path,                users, max p95 (ms), max errors (%)
    ("/api/products",         10,  300,          1),
    ("/api/search?q=book",    10,  300,          1),
    ("/api/report",           10,  1000,         1),
]  # fmt: skip


@pytest.mark.parametrize(("path", "users", "max_p95", "max_errors"), TARGETS)
def test_page_is_fast_enough(path, users, max_p95, max_errors):
    result = run(f"{BASE_URL}{path}", users=users, seconds=SECONDS)
    print(report(path, users, result))  # shown with -s, or for a failed test
    errors, p95 = result.error_percent, result.percentile(95)
    assert errors <= max_errors, f"{errors:.1f}% errors: {dict(result.statuses)}"
    assert p95 <= max_p95, f"p95 is {p95:.0f} ms, target {max_p95} ms"
