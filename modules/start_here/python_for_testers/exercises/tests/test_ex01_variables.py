# Template from myOpenSDET: https://myopensdet.github.io/
from ex01_variables import is_adult, to_cents


def test_price_with_cents():
    assert to_cents("12.50") == 1250


def test_price_with_one_decimal():
    assert to_cents("12.5") == 1250


def test_price_without_decimals():
    assert to_cents("7") == 700


def test_adult_at_the_edge():
    assert is_adult(18) is True
    assert is_adult(17) is False
