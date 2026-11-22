# Template from myOpenSDET: https://myopensdet.github.io/
"""Each test fails on purpose. Run: python -m pytest assert_demo"""


def test_total_is_wrong():
    total = 425 * 2 + 150
    assert total == 1100


def test_response_has_a_different_price():
    expected = {"id": 7, "name": "Pocket notebook", "price": 425}
    actual = {"id": 7, "name": "Pocket notebook", "price": 450}
    assert actual == expected
