# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""The same tests, with every mistake fixed."""

import pytest


def add_item(item, cart=None):
    if not item:
        raise ValueError("Item name can't be empty")
    if cart is None:
        cart = []
    cart.append(item)
    return cart


def test_adding_one_item():
    cart = add_item("book")
    assert len(cart) == 1, "the cart should have one item"


def test_adding_to_a_new_cart():
    cart = add_item("pen")
    assert cart == ["pen"]


def test_empty_name_is_refused():
    with pytest.raises(ValueError, match="can't be empty"):
        add_item("")


def test_missing_discount():
    discount = None
    assert discount is None
