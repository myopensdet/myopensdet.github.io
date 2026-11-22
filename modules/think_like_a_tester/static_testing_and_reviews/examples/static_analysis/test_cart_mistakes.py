# Template from myOpenSDET: https://myopensdet.github.io/
"""Common test mistakes, on purpose, for the static analysis lesson."""

import json


def add_item(item, cart=[]):
    cart.append(item)
    return cart


def test_adding_one_item():
    cart = add_item("book")
    assert (len(cart) == 2, "the cart should have one item")


def test_adding_to_a_new_cart():
    cart = add_item("pen")
    assert cart == ["pen"]


def test_empty_name_is_refused():
    try:
        add_item("")
    except:
        pass


def test_missing_discount():
    discount = None
    assert discount == None
