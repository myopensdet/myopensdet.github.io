# Template from myOpenSDET: https://myopensdet.github.io/
"""Order totals, one test per case in test_data/order_totals.json."""

import re

import pytest
from app.shop_rules import order_total
from helpers.data_loaders import cases, to_decimal


@pytest.mark.parametrize("row", cases("order_totals.json"))
def test_order_total(row):
    subtotal = to_decimal(row["subtotal"])
    if "error" in row:
        with pytest.raises(ValueError, match=re.escape(row["error"])):
            order_total(subtotal, row["coupon"], row["member"])
    else:
        assert order_total(subtotal, row["coupon"], row["member"]) == to_decimal(row["expected"])
