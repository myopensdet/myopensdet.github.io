# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Logging in, through the form. The other tests log in through the API instead."""

import pytest
from pages import LoginPage
from playwright.sync_api import expect

from tests.conftest import TEST_USER


@pytest.mark.smoke
def test_log_in_with_the_test_account(page):
    books = LoginPage(page).open().log_in(TEST_USER["email"], TEST_USER["password"])
    expect(books.heading).to_be_visible()
    expect(page).to_have_url("/books")


def test_wrong_password_shows_an_error(page):
    login = LoginPage(page).open()
    login.log_in(TEST_USER["email"], "not-the-password")
    expect(login.error).to_have_text("Wrong email or password")


def test_log_out_goes_back_to_the_login_page(logged_in_page):
    from pages import BooksPage  # noqa: PLC0415

    login = BooksPage(logged_in_page).open().header.log_out()
    expect(login.log_in_button).to_be_visible()
