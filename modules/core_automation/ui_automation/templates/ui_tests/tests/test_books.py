# Template from myOpenSDET: https://myopensdet.github.io/
"""The book list loads after the page. expect() waits for it; nothing here sleeps."""

import pytest
from pages import BooksPage
from playwright.sync_api import expect


@pytest.mark.smoke
def test_all_books_are_listed(logged_in_page):
    books = BooksPage(logged_in_page).open()
    expect(books.results).to_have_count(4)


def test_search_finds_matching_books(logged_in_page):
    books = BooksPage(logged_in_page).open().search("test")
    expect(books.results).to_have_count(2)
    expect(books.results.get_by_role("heading")).to_have_text(["Python for Testers", "Clean Tests"])


def test_search_with_no_match_says_so(logged_in_page):
    books = BooksPage(logged_in_page).open().search("cooking")
    expect(books.status).to_have_text('No books match "cooking"')
    expect(books.results).to_have_count(0)


def test_add_to_cart_updates_the_cart_count(logged_in_page):
    books = BooksPage(logged_in_page).open()
    books.add_to_cart("SQL in a Week")
    books.add_to_cart("SQL in a Week")
    expect(books.header.cart_count).to_have_text("2")
    expect(books.status).to_have_text("Added SQL in a Week to your cart")
