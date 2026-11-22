# Template from myOpenSDET: https://myopensdet.github.io/
"""Checkout: a form with a select and radio buttons, a card field in an iframe, a new tab."""

import re

import pytest
from pages import CheckoutPage
from playwright.sync_api import expect

TEST_CARD = "4242 4242 4242 4242"  # a fake card number; the practice shop charges nothing


@pytest.fixture
def checkout(cart_with_books):
    return CheckoutPage(cart_with_books).open()


@pytest.mark.smoke
def test_place_an_order(checkout):
    checkout.fill_details("Arshad Test", "Germany", delivery="Express (4.99)")
    order = checkout.pay_with(TEST_CARD).accept_terms().place_order()
    expect(order.heading).to_be_visible()
    expect(order.number).to_have_text(re.compile(r"BK-\d+"))
    expect(order.page.get_by_text("Total paid: 68.98")).to_be_visible()
    expect(order.header.cart_count).to_have_text("0")


def test_order_needs_the_terms_accepted(checkout):
    checkout.fill_details("Arshad Test", "Germany").pay_with(TEST_CARD).place_order()
    expect(checkout.error).to_have_text("Please accept the terms of sale")


def test_card_number_must_have_16_digits(checkout):
    checkout.fill_details("Arshad Test", "Germany").pay_with("4242").accept_terms().place_order()
    expect(checkout.error).to_have_text("Card number must have 16 digits")


def test_terms_open_in_a_new_tab(checkout):
    terms = checkout.open_terms()
    expect(terms.get_by_role("heading", name="Terms of sale")).to_be_visible()
    expect(checkout.place_order_button).to_be_visible()  # the checkout tab is still there
