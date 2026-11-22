# Template from myOpenSDET: https://myopensdet.github.io/
"""Tests for the practice cart. Three of them fail, each for a different reason."""

from shop.cart import Cart


def test_empty_cart_costs_nothing():
    assert Cart().total() == 0


def test_one_book():
    cart = Cart()
    cart.add("Python book", 24.50)
    assert cart.total() == 24.50


def test_two_cheap_items():
    cart = Cart()
    cart.add("Pen", 0.10)
    cart.add("Pencil", 0.20)
    assert cart.total() == 0.30


def test_discount_code_typed_in_small_letters():
    cart = Cart()
    cart.add("Python book", 50.00)
    assert cart.total("welcome10") == 45.00


def test_unknown_discount_code_gives_no_discount():
    cart = Cart()
    cart.add("Python book", 50.00)
    assert cart.total("SPRING") == 50.00
