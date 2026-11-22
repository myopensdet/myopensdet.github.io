# Template from myOpenSDET: https://myopensdet.github.io/
"""Checkout: the form checks its fields, the totals add up, the order is placed."""

import pytest
from playwright.sync_api import Page, expect

from tests.conftest import add_to_cart, money

PRODUCTS = ["Sauce Labs Backpack", "Sauce Labs Bike Light"]  # CHANGE: your products
FORM = {"First Name": "Arshad", "Last Name": "Test", "Zip/Postal Code": "1207"}


def open_checkout_form(page: Page) -> None:
    for product in PRODUCTS:
        add_to_cart(page, product)
    page.get_by_test_id("shopping-cart-link").click()
    page.get_by_role("button", name="Checkout").click()


def fill_form(page: Page, **changes: str) -> None:
    for label, value in (FORM | changes).items():
        page.get_by_placeholder(label).fill(value)


@pytest.mark.parametrize(
    ("empty", "message"),
    [
        ("First Name", "First Name is required"),
        ("Last Name", "Last Name is required"),
        ("Zip/Postal Code", "Postal Code is required"),
    ],
)
def test_each_required_field_shows_an_error(logged_in: Page, empty, message):
    open_checkout_form(logged_in)
    fill_form(logged_in, **{empty: ""})
    logged_in.get_by_role("button", name="Continue").click()
    expect(logged_in.get_by_test_id("error")).to_contain_text(message)


def test_form_keeps_what_was_typed(logged_in: Page):
    open_checkout_form(logged_in)
    fill_form(logged_in)
    for label, value in FORM.items():
        expect(logged_in.get_by_placeholder(label)).to_have_value(value)


def test_totals_add_up(logged_in: Page):
    open_checkout_form(logged_in)
    fill_form(logged_in)
    logged_in.get_by_role("button", name="Continue").click()
    expect(logged_in.get_by_test_id("total-label")).to_be_visible()  # wait for the next page
    prices = [money(p) for p in logged_in.get_by_test_id("inventory-item-price").all_inner_texts()]
    subtotal = money(logged_in.get_by_test_id("subtotal-label").inner_text())
    tax = money(logged_in.get_by_test_id("tax-label").inner_text())
    total = money(logged_in.get_by_test_id("total-label").inner_text())
    assert subtotal == pytest.approx(sum(prices))
    assert total == pytest.approx(subtotal + tax)


def test_order_is_placed_and_the_cart_is_emptied(logged_in: Page):
    open_checkout_form(logged_in)
    fill_form(logged_in)
    logged_in.get_by_role("button", name="Continue").click()
    logged_in.get_by_role("button", name="Finish").click()
    expect(logged_in.get_by_test_id("complete-header")).to_have_text("Thank you for your order!")
    expect(logged_in.get_by_test_id("shopping-cart-badge")).to_have_count(0)
