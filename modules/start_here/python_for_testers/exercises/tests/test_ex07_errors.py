# Template from myOpenSDET: https://myopensdet.github.io/
import pytest
from ex07_errors import parse_age, safe_int


def test_parse_age():
    assert parse_age("30") == 30


def test_parse_age_explains_the_problem():
    with pytest.raises(ValueError, match="Age must be a whole number, got 'abc'"):
        parse_age("abc")


def test_safe_int():
    assert safe_int("42") == 42
    assert safe_int("forty-two") == 0
    assert safe_int("", default=-1) == -1
