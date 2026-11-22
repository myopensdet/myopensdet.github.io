# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Page tests. A failed one gets a screenshot in the HTML report (see conftest.py)."""

import logging

import pytest
from playwright.sync_api import expect

log = logging.getLogger("tests.pages")


@pytest.fixture
def cart_page(page):
    for book in ["Python for Testers", "SQL in a Week", "SQL in a Week"]:
        assert page.request.post("/api/cart", data={"book": book}).ok
    log.info("Cart filled through the API: 3 books")
    page.goto("/cart")
    return page


def test_cart_page_shows_the_total(cart_page):
    expect(cart_page.get_by_test_id("cart-total")).to_have_text("63.99")


@pytest.mark.xfail(
    reason="Known bug: the cart count stays the same after Remove", raises=AssertionError
)
def test_remove_updates_the_cart_count(cart_page):
    row = cart_page.get_by_role("row").filter(has_text="SQL in a Week")
    row.get_by_role("button", name="Remove").click()
    log.info("Removed SQL in a Week")
    expect(cart_page.get_by_test_id("cart-count")).to_have_text("1")
