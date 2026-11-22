# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Login: the right user gets in, everyone else sees a clear message."""

import re

from playwright.sync_api import Page, expect

from tests.conftest import USERNAME, log_in


def test_valid_login_opens_the_products_page(logged_in: Page):
    expect(logged_in.get_by_test_id("title")).to_have_text("Products")


def test_wrong_password_shows_an_error(page: Page):
    log_in(page, USERNAME or "any_user", "wrong_password")
    expect(page.get_by_test_id("error")).to_contain_text("do not match")
    expect(page).not_to_have_url(re.compile("inventory"))


def test_empty_username_shows_an_error(page: Page):
    log_in(page, "", "")
    expect(page.get_by_test_id("error")).to_contain_text("Username is required")


def test_pages_need_a_login(page: Page):
    page.goto("/inventory.html")
    expect(page.get_by_test_id("error")).to_contain_text("when you are logged in")


def test_logout_returns_to_the_login_page(logged_in: Page):
    logged_in.get_by_role("button", name="Open Menu").click()
    logged_in.get_by_test_id("logout-sidebar-link").click()
    expect(logged_in.get_by_role("button", name="Login")).to_be_visible()
