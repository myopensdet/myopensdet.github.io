# Template from myOpenSDET: https://myopensdet.github.io/
"""Shared setup for the UI tests. pytest-playwright gives every test a fresh `page`
(a new, empty browser profile), so tests never share a login or a cart.

Change the four parts marked CHANGE for your own app."""

import os

import pytest
from playwright.sync_api import Page, expect

# CHANGE 1: the address of the site you test (or set BASE_URL in the terminal).
BASE_URL = os.environ.get("BASE_URL", "https://www.saucedemo.com")

# CHANGE 2: who logs in. Set these in the terminal, never in a file:
#   export APP_USERNAME=...  and  export APP_PASSWORD=...
USERNAME = os.environ.get("APP_USERNAME", "")
PASSWORD = os.environ.get("APP_PASSWORD", "")

# CHANGE 3: the attribute your developers put on elements for tests.
# Playwright's default is data-testid. This shop uses data-test.
TEST_ID_ATTRIBUTE = "data-test"

expect.set_options(timeout=5_000)  # how long expect() waits for the page to match


@pytest.fixture(scope="session")
def base_url() -> str:
    """Every page.goto("/...") and expect(page).to_have_url("/...") starts from here."""
    return BASE_URL


@pytest.fixture(scope="session", autouse=True)
def test_ids(playwright):
    playwright.selectors.set_test_id_attribute(TEST_ID_ATTRIBUTE)


def log_in(page: Page, username: str, password: str) -> None:
    """CHANGE 4: the steps of your login page."""
    page.goto("/")
    page.get_by_placeholder("Username").fill(username)
    page.get_by_placeholder("Password").fill(password)
    page.get_by_role("button", name="Login").click()


@pytest.fixture
def logged_in(page: Page) -> Page:
    """A page that is already logged in. Skips the test if no login is set."""
    if not (USERNAME and PASSWORD):
        pytest.skip("Set APP_USERNAME and APP_PASSWORD to run tests that need a login")
    log_in(page, USERNAME, PASSWORD)
    expect(page).to_have_url("/inventory.html")
    return page


def add_to_cart(page: Page, product: str) -> None:
    page.get_by_test_id("inventory-item").filter(has_text=product).get_by_role(
        "button", name="Add to cart"
    ).click()


def money(text: str) -> float:
    """'$29.99' or 'Total: $43.18' -> 29.99 or 43.18"""
    return float(text.split("$")[-1])
