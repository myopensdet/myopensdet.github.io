# Template from myOpenSDET: https://myopensdet.github.io/
"""Boundary values: test right at each edge, and one step past it."""

import pytest
from shop.signup import check_signup

AGE_ERROR = "Age must be 18 to 120"
NAME_LENGTH_ERROR = "Username must be 3 to 20 characters"


@pytest.mark.parametrize(
    ("age", "expected"),
    [
        (17, [AGE_ERROR]),
        (18, []),
        (120, []),
        (121, [AGE_ERROR]),
    ],
)
def test_age_at_the_edges(age, expected):
    assert check_signup("arshad", age) == expected


@pytest.mark.parametrize(
    ("length", "expected"),
    [
        (2, [NAME_LENGTH_ERROR]),
        (3, []),
        (20, []),
        (21, [NAME_LENGTH_ERROR]),
    ],
)
def test_username_length_at_the_edges(length, expected):
    assert check_signup("a" * length, 30) == expected
