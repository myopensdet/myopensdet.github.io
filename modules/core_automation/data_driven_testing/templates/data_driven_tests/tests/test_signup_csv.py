# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Signup rules, one test per row of test_data/signup_cases.csv."""

import pytest
from app.shop_rules import check_signup
from helpers.data_loaders import cases, to_int


@pytest.mark.parametrize("row", cases("signup_cases.csv"))
def test_signup_rules(row):
    problems = check_signup(row["email"], row["password"], to_int(row["age"]))
    assert problems == row["expected_problems"].split()
