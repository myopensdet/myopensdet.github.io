# Template from myOpenSDET: https://myopensdet.github.io/
"""UI test: drive a real browser, like a user. Slowest and most fragile, so keep only a few.

It runs only when Playwright is installed and SHOP_URL points at a running shop:
    pip install pytest-playwright && playwright install chromium
    SHOP_URL=http://127.0.0.1:8080 pytest tests/ui
"""

import os

import pytest

SHOP_URL = os.environ.get("SHOP_URL")
pytestmark = pytest.mark.skipif(
    not SHOP_URL, reason="set SHOP_URL to a running shop (and install pytest-playwright)"
)


def test_checkout_shows_free_shipping_at_50_dollars(page):
    page.goto(f"{SHOP_URL}/cart")
    page.get_by_label("Quantity").fill("2")
    page.get_by_role("button", name="Update cart").click()
    assert page.get_by_test_id("shipping").inner_text() == "$0.00"
