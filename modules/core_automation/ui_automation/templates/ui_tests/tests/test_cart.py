# Template from myOpenSDET: https://myopensdet.github.io/
"""The cart page. The cart is filled through the API first (fixture cart_with_books)."""

import pytest
from pages import CartPage
from playwright.sync_api import expect


def test_cart_shows_each_book_and_the_total(cart_with_books):
    cart = CartPage(cart_with_books).open()
    expect(cart.rows).to_have_count(2)
    expect(cart.row("SQL in a Week")).to_contain_text("39.00")
    expect(cart.total).to_have_text("63.99")


def test_remove_a_book_updates_the_total(cart_with_books):
    cart = CartPage(cart_with_books).open().remove("SQL in a Week")
    expect(cart.rows).to_have_count(1)
    expect(cart.total).to_have_text("24.99")


@pytest.mark.xfail(
    reason="Known bug: the cart count stays the same after Remove", raises=AssertionError
)
def test_remove_a_book_updates_the_cart_count(cart_with_books):
    cart = CartPage(cart_with_books).open()
    expect(cart.header.cart_count).to_have_text("3")
    cart.remove("SQL in a Week")
    expect(cart.header.cart_count).to_have_text("1")


def test_empty_cart_asks_first_then_empties_it(cart_with_books):
    cart = CartPage(cart_with_books).open().empty_cart(confirm=True)
    expect(cart.empty_message).to_be_visible()
    expect(cart.header.cart_count).to_have_text("0")


def test_empty_cart_keeps_the_books_when_you_cancel(cart_with_books):
    cart = CartPage(cart_with_books).open().empty_cart(confirm=False)
    expect(cart.rows).to_have_count(2)
