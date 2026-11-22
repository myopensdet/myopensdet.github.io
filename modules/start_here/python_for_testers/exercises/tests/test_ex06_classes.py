# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
from ex06_classes import Cart


def test_new_cart_is_empty():
    cart = Cart()
    assert cart.count() == 0
    assert cart.total() == 0


def test_cart_counts_quantities():
    cart = Cart()
    cart.add("Pen", 1.5, quantity=3)
    cart.add("Notebook", 4.25)
    assert cart.count() == 4
    assert cart.total() == 8.75


def test_two_carts_are_separate():
    first, second = Cart(), Cart()
    first.add("Pen", 1.5)
    assert second.count() == 0
