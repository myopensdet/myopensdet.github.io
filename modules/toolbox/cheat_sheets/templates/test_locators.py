# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Every line of the locators cheat sheet, run on locator_practice.html.

Needs: pip install pytest-playwright, then: playwright install chromium
Run:   python -m pytest test_locators.py -v

The page is served at a pretend address (page.route), so nothing goes on the internet.
"""

import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

HTML = Path(__file__).with_name("locator_practice.html").read_text(encoding="utf-8")
URL = "https://shop.example.com/orders/7"


@pytest.fixture
def shop(page: Page) -> Page:
    page.route(
        "https://shop.example.com/**",
        lambda route: route.fulfill(body=HTML, content_type="text/html"),
    )
    page.goto(URL)
    return page


def test_find(shop: Page):
    page = shop
    for locator in [
        page.get_by_role("button", name="Save"),
        page.get_by_role("heading", name="Practice shop"),
        page.get_by_role("link", name="Help"),
        page.get_by_role("checkbox", name="Send me news"),
        page.get_by_label("Email"),
        page.get_by_placeholder("you@example.com"),
        page.get_by_text("Last saved"),
        page.get_by_alt_text("Shop logo"),
        page.get_by_title("Saved at 10:00"),
        page.get_by_test_id("save-button"),
        page.get_by_text("Last saved: today", exact=True),
    ]:
        expect(locator).to_have_count(1)
    expect(page.locator(".product .price")).to_have_count(3)


def test_narrow(shop: Page):
    page = shop
    expect(page.get_by_role("listitem").filter(has_text="Test mug")).to_contain_text("9.99")
    button = (
        page.get_by_role("listitem")
        .filter(has_text="Test mug")
        .get_by_role("button", name="Add to cart")
    )
    expect(button).to_be_enabled()
    sold_out = page.locator(".product").filter(has=page.get_by_role("button", name="Sold out"))
    expect(sold_out).to_contain_text("Bug sticker")
    expect(page.get_by_role("link", name=re.compile(r"^Cart"))).to_have_text("Cart (2)")
    expect(page.locator(".price").first).to_have_text("24.50")
    expect(page.locator(".price").last).to_have_text("1.50")
    expect(page.locator(".price").nth(1)).to_have_text("9.99")


def test_act_and_check(shop: Page):
    page = shop
    page.get_by_label("Email").fill("arshad.test@example.com")
    page.get_by_role("checkbox", name="Send me news").check()
    page.get_by_label("Country").select_option("United Kingdom")
    page.get_by_label("Email").press("Enter")
    page.get_by_test_id("save-button").click()

    expect(page.get_by_role("alert")).to_be_visible()
    expect(page.get_by_role("heading", name="Practice shop")).to_have_text("Practice shop")
    expect(page.get_by_title("Saved at 10:00")).to_contain_text("today")
    expect(page.locator(".product")).to_have_count(3)
    expect(page.get_by_label("Email")).to_have_value("arshad.test@example.com")
    expect(page.get_by_role("checkbox", name="Send me news")).to_be_checked()
    expect(page.get_by_role("button", name="Sold out")).to_be_disabled()
    expect(page.get_by_label("Email")).to_have_attribute("type", "email")
    expect(page.get_by_label("Country")).to_have_value("United Kingdom")
    expect(page).to_have_title("Locator practice")
    expect(page).to_have_url(re.compile(r"/orders/\d+"))
