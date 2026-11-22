# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Unit tests: one function at a time, no database, no web. Each one runs in a blink."""

import pytest
from shop.money import discount, shipping_cost


@pytest.mark.parametrize(
    ("subtotal", "expected"),
    [(0, 0), (1, 499), (4999, 499), (5000, 0), (5001, 0)],
)
def test_free_shipping_from_50_dollars(subtotal, expected):
    assert shipping_cost(subtotal) == expected


def test_save10_takes_ten_percent_off():
    assert discount(5000, "SAVE10") == 500


def test_an_unknown_coupon_is_refused():
    with pytest.raises(ValueError, match="Unknown coupon"):
        discount(5000, "FREE100")
