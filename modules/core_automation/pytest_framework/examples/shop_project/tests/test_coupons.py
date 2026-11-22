# Template from myOpenSDET: https://myopensdet.github.io/
"""Parametrize: one test, many rows of data."""

import pytest


@pytest.mark.parametrize(
    ("subtotal", "code", "expected_total"),
    [
        pytest.param(2000, "WELCOME5", 1500, id="welcome5-at-the-minimum"),
        pytest.param(3500, "WELCOME5", 3000, id="welcome5-above-the-minimum"),
        pytest.param(400, "SAVE10", 360, id="save10"),
        pytest.param(155, "SAVE10", 140, id="save10-rounds-in-the-shop's-favour"),
        pytest.param(2000, " welcome5 ", 1500, id="spaces-and-lower-case"),
    ],
)
def test_coupon_lowers_the_total(cart, subtotal, code, expected_total):
    cart.add("Gift card", subtotal)
    cart.apply_coupon(code)
    assert cart.total() == expected_total


@pytest.mark.parametrize(
    ("subtotal", "code", "message"),
    [
        (1999, "WELCOME5", "WELCOME5 needs an order of at least 20.00"),
        (2000, "WELCOME10", "Unknown coupon: WELCOME10"),
        (2000, "", "Unknown coupon: "),
    ],
)
def test_coupon_is_refused(cart, subtotal, code, message):
    cart.add("Gift card", subtotal)
    with pytest.raises(ValueError, match=message):
        cart.apply_coupon(code)
    assert cart.total() == subtotal


@pytest.mark.nightly
@pytest.mark.parametrize("quantity", range(1, 51))
def test_total_for_many_quantities(cart, quantity):
    cart.add("Pen", 150, quantity=quantity)
    assert cart.total() == 150 * quantity
