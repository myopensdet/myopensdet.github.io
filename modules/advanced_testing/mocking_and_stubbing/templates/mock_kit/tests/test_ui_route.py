# Template from myOpenSDET: https://myopensdet.github.io/
"""Level 3, in the browser: Playwright answers the page's API calls itself (page.route).

Shows every message the page can show, without a backend that can fail on demand.
Needs: pip install pytest-playwright, then: playwright install chromium
"""

import json
from pathlib import Path

import pytest
from playwright.sync_api import Page, Route, expect

PAGE = (Path(__file__).resolve().parents[1] / "ui" / "checkout.html").read_text(encoding="utf-8")
SHOP = "https://shop.example.com"  # a pretend address: nothing goes on the internet


@pytest.fixture
def checkout_page(page: Page) -> Page:
    page.route(f"{SHOP}/checkout", lambda route: route.fulfill(body=PAGE, content_type="text/html"))
    return page


def answer(status: int, message: str):
    def handler(route: Route):
        route.fulfill(status=status, json={"message": message})

    return handler


@pytest.mark.parametrize(
    ("status", "message"),
    [
        (200, "Paid. Receipt ch_test_1001."),
        (402, "Your card was declined (insufficient_funds)."),
        (503, "We couldn't reach the payment service. Your order is saved: try again."),
    ],
)
def test_page_shows_each_answer(checkout_page: Page, status, message):
    checkout_page.route(f"{SHOP}/api/pay", answer(status, message))
    checkout_page.goto(f"{SHOP}/checkout")
    checkout_page.get_by_role("button", name="Pay £24.49").click()
    expect(checkout_page.get_by_role("status")).to_have_text(message)


def test_no_connection(checkout_page: Page):
    checkout_page.route(f"{SHOP}/api/pay", lambda route: route.abort("internetdisconnected"))
    checkout_page.goto(f"{SHOP}/checkout")
    checkout_page.get_by_role("button", name="Pay £24.49").click()
    expect(checkout_page.get_by_role("status")).to_have_text(
        "No connection. Your order is saved: try again."
    )


def test_page_sends_the_order_id(checkout_page: Page):
    sent = []

    def record(route: Route):
        sent.append(json.loads(route.request.post_data))
        route.fulfill(json={"message": "Paid. Receipt ch_test_1001."})

    checkout_page.route(f"{SHOP}/api/pay", record)
    checkout_page.goto(f"{SHOP}/checkout")
    checkout_page.get_by_role("button", name="Pay £24.49").click()
    expect(checkout_page.get_by_role("status")).to_have_text("Paid. Receipt ch_test_1001.")
    assert sent == [{"order_id": 101}]
