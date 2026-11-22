# Template from myOpenSDET: https://myopensdet.github.io/
"""Equivalence partitioning: one value from each group stands in for the whole group."""

import pytest
from shop.signup import check_signup

AGE_ERROR = "Age must be 18 to 120"
NAME_LENGTH_ERROR = "Username must be 3 to 20 characters"
NAME_CHARACTERS_ERROR = "Username can only use letters and numbers"


@pytest.mark.parametrize(
    ("age", "expected"),
    [
        (10, [AGE_ERROR]),  # group: too young
        (30, []),  # group: allowed
        (150, [AGE_ERROR]),  # group: too old
    ],
)
def test_one_age_from_each_group(age, expected):
    assert check_signup("arshad", age) == expected


@pytest.mark.parametrize(
    ("username", "expected"),
    [
        ("", [NAME_LENGTH_ERROR]),  # group: empty
        ("al", [NAME_LENGTH_ERROR]),  # group: too short
        ("arshad", []),  # group: allowed
        ("a" * 30, [NAME_LENGTH_ERROR]),  # group: too long
        ("ars had", [NAME_CHARACTERS_ERROR]),  # group: right length, wrong characters
    ],
)
def test_one_username_from_each_group(username, expected):
    assert check_signup(username, 30) == expected
