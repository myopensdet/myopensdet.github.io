# Template from myOpenSDET: https://myopensdet.github.io/
from ex01_variables import is_fast_enough, parse_status, to_cents


def test_status_text_becomes_a_number():
    assert parse_status("200") == 200
    assert parse_status("404") == 404


def test_status_with_spaces_from_a_file():
    assert parse_status(" 201\n") == 201


def test_fast_enough_at_the_limit():
    assert is_fast_enough(1.0, 1.0) is True
    assert is_fast_enough(0.45, 1.0) is True
    assert is_fast_enough(1.2, 1.0) is False


def test_price_in_cents():
    assert to_cents(4.25) == 425
    assert to_cents(19.99) == 1999


def test_cents_fix_the_decimal_problem():
    assert to_cents(0.10 + 0.20) == to_cents(0.30)
