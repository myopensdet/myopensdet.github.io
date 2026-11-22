# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Decision table: one test per row. The table is the test."""

import pytest
from shop.delivery import delivery_fee

OVER = 6000  # an order of $60.00: "$50 or more" is Yes
UNDER = 2000  # an order of $20.00: "$50 or more" is No


@pytest.mark.parametrize(
    ("row", "member", "subtotal", "express", "fee"),
    [
        (1, True, OVER, True, 499),
        (2, True, OVER, False, 0),
        (3, True, UNDER, True, 499),
        (4, True, UNDER, False, 0),
        (5, False, OVER, True, 999),
        (6, False, OVER, False, 0),
        (7, False, UNDER, True, 999),
        (8, False, UNDER, False, 499),
    ],
)
def test_delivery_fee_table(row, member, subtotal, express, fee):
    assert delivery_fee(subtotal, member=member, express=express) == fee, f"row {row}"
