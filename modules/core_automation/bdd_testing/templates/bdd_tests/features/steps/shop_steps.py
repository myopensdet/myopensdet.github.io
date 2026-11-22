# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""behave steps. Each step says what a shopper does or sees; the driver does the work."""

from decimal import Decimal

from behave import given, then, when


@given("an empty cart")
def step_empty_cart(context):
    context.shop.start_empty_cart()


@given('I add {copies:d} copy of "{book}"')
@given('I add {copies:d} copies of "{book}"')
@when('I add {copies:d} copy of "{book}"')
@when('I add {copies:d} copies of "{book}"')
def step_add_book(context, copies, book):
    context.shop.add_book(book, copies)


@when('I apply the coupon "{code}"')
def step_apply_coupon(context, code):
    context.shop.apply_coupon(code)


@then("the cart total is {amount}")
def step_total_is(context, amount):
    actual = context.shop.total()
    assert actual == Decimal(amount), f"Expected total {amount}, got {actual}"


@then('I see the message "{text}"')
def step_message_is(context, text):
    actual = context.shop.message()
    assert actual == text, f'Expected message "{text}", got "{actual}"'
