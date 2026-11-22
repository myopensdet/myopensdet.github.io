# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""pytest-bdd steps for the same feature files behave uses. Every scenario becomes a test."""

from decimal import Decimal

from pytest_bdd import given, parsers, scenarios, then, when

scenarios(".")  # every .feature file in bdd_features_base_dir (features/)


@given("an empty cart")
def empty_cart(shop):
    shop.start_empty_cart()


@given(parsers.parse('I add {copies:d} copy of "{book}"'))
@given(parsers.parse('I add {copies:d} copies of "{book}"'))
@when(parsers.parse('I add {copies:d} copy of "{book}"'))
@when(parsers.parse('I add {copies:d} copies of "{book}"'))
def add_book(shop, copies, book):
    shop.add_book(book, copies)


@when(parsers.parse('I apply the coupon "{code}"'))
def apply_coupon(shop, code):
    shop.apply_coupon(code)


@then(parsers.parse("the cart total is {amount}"))
def total_is(shop, amount):
    actual = shop.total()
    assert actual == Decimal(amount), f"Expected total {amount}, got {actual}"


@then(parsers.parse('I see the message "{text}"'))
def message_is(shop, text):
    actual = shop.message()
    assert actual == text, f'Expected message "{text}", got "{actual}"'
