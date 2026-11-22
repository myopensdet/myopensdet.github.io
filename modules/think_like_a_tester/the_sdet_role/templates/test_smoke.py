# Template from myOpenSDET: https://myopensdet.github.io/
"""Smoke tests: the quickest check that a deployed app is up and answering.

Run them right after every deploy, before any longer test suite. If they fail,
stop: there is no point running hundreds of other tests.

Set these before you run (only BASE_URL is required):
    BASE_URL            the app's address, e.g. https://staging.your-company.example
    HEALTH_PATH         the health check address (default /health)
    SMOKE_PAGES         pages that must load, separated by commas (default /)
    SMOKE_MAX_SECONDS   the slowest answer you accept (default 2)

    BASE_URL=https://staging.your-company.example pytest test_smoke.py -v

Uses only Python's standard library and pytest. If your project already uses
requests or httpx, you can swap get() for them.
"""

from __future__ import annotations

import os
import time
import urllib.error
import urllib.request

import pytest

BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
HEALTH_PATH = os.environ.get("HEALTH_PATH", "/health")
PAGES = [page.strip() for page in os.environ.get("SMOKE_PAGES", "/").split(",") if page.strip()]
MAX_SECONDS = float(os.environ.get("SMOKE_MAX_SECONDS", "2"))
TIMEOUT_SECONDS = 10

pytestmark = pytest.mark.skipif(
    not BASE_URL, reason="set BASE_URL, e.g. BASE_URL=https://staging.your-company.example"
)


def get(path: str) -> tuple[int, str, float]:
    """Return the status code, the body and how many seconds the answer took."""
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(BASE_URL + path, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310  (the URL comes from you)
            status, body = response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:  # 4xx and 5xx still have a status and a body
        status, body = error.code, error.read().decode("utf-8", "replace")
    return status, body, time.perf_counter() - start


def test_health_check_says_ok():
    status, body, _ = get(HEALTH_PATH)
    assert status == 200, f"{HEALTH_PATH} answered {status}: {body[:200]}"


def test_health_check_is_fast():
    _, _, seconds = get(HEALTH_PATH)
    assert seconds <= MAX_SECONDS, f"{HEALTH_PATH} took {seconds:.2f}s (limit {MAX_SECONDS}s)"


@pytest.mark.parametrize("path", PAGES)
def test_page_loads(path):
    status, body, _ = get(path)
    assert status == 200, f"{path} answered {status}"
    assert body.strip(), f"{path} answered 200 with an empty page"
