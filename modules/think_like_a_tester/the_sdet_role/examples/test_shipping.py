# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Automated checks for the shipping rule, at the edges where bugs hide."""

import pytest
from shipping import shipping_cost


@pytest.mark.parametrize(
    ("subtotal", "expected"),
    [
        (0, 0),  # empty cart: nothing to ship
        (1, 499),  # $0.01: the smallest real order pays shipping
        (4999, 499),  # $49.99: one cent under the line
        (5000, 0),  # $50.00: exactly on the line, ships free
        (5001, 0),  # $50.01: just over the line
    ],
)
def test_free_shipping_from_50_dollars(subtotal, expected):
    assert shipping_cost(subtotal) == expected
