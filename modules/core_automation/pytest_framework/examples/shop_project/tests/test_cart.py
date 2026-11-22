# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Tests and asserts, with fixtures from conftest.py."""

import pytest


@pytest.mark.smoke
def test_new_cart_is_empty(cart):
    assert cart.count() == 0
    assert cart.total() == 0


@pytest.mark.smoke
def test_total_of_two_items(cart_with_items):
    assert cart_with_items.count() == 3
    assert cart_with_items.total() == 1000


def test_items_keep_their_order(cart_with_items):
    names = [item["name"] for item in cart_with_items.items]
    assert names == ["Pocket notebook", "Pen"]


def test_quantity_zero_is_refused(cart):
    with pytest.raises(ValueError, match="Quantity must be 1 or more, got 0"):
        cart.add("Pen", 150, quantity=0)


def test_saved_order_is_in_the_store(cart_with_items, order_store):
    order_store.append({"total": cart_with_items.total()})
    assert order_store == [{"total": 1000}]
