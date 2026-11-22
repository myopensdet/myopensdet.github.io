# Template from myOpenSDET: https://myopensdet.github.io/
"""The business team's discount rules, straight from their Excel sheet."""

import pytest
from app.shop_rules import order_total
from helpers.data_loaders import cases, to_bool, to_decimal


@pytest.mark.parametrize("row", cases("discount_rules.xlsx", sheet="Discounts", id_field="rule"))
def test_discount_rule(row):
    total = order_total(to_decimal(row["subtotal"]), row["coupon"], to_bool(row["member"]))
    assert total == to_decimal(row["expected_total"])
