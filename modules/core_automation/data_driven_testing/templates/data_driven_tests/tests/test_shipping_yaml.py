# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Shipping prices, one test per case in test_data/shipping_cases.yaml."""

import re

import pytest
from app.shop_rules import shipping_cost
from helpers.data_loaders import cases, to_decimal


@pytest.mark.parametrize("row", cases("shipping_cases.yaml"))
def test_shipping_cost(row):
    weight = to_decimal(row["weight_kg"])
    if "error" in row:
        with pytest.raises(ValueError, match=re.escape(row["error"])):
            shipping_cost(row["country"], weight)
    else:
        assert shipping_cost(row["country"], weight) == to_decimal(row["expected"])
