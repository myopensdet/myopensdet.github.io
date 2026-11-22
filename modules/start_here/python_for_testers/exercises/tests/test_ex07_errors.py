# Template from myOpenSDET: https://myopensdet.github.io/
import pytest
from ex07_errors import parse_battery, safe_int


def test_parse_battery():
    assert parse_battery("87") == 87
    assert parse_battery("0") == 0
    assert parse_battery("100") == 100


def test_parse_battery_explains_text():
    with pytest.raises(ValueError, match="Battery must be a whole number from 0 to 100, got 'low'"):
        parse_battery("low")


@pytest.mark.parametrize("text", ["101", "-1"])
def test_parse_battery_explains_out_of_range(text):
    with pytest.raises(ValueError, match=f"got '{text}'"):
        parse_battery(text)


def test_safe_int():
    assert safe_int("42") == 42
    assert safe_int("forty-two") == 0
    assert safe_int("", default=-1) == -1
