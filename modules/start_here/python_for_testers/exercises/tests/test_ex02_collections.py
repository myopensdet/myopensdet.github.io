# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
from ex02_collections import clean_username, first_and_last, price_of


def test_clean_username():
    assert clean_username("  Admin ") == "admin"


def test_first_and_last():
    assert first_and_last(["login", "search", "pay"]) == ("login", "pay")


def test_first_and_last_of_one_item():
    assert first_and_last(["login"]) == ("login", "login")


def test_price_of():
    assert price_of({"name": "Pen", "price": 1.5}) == 1.5
    assert price_of({"name": "Free sticker"}) == 0
