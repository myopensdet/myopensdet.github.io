# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Integration tests: several parts together. Here, the cart with the money rules."""

from shop.cart import Cart


def test_two_books_reach_free_shipping():
    cart = Cart()
    cart.add("Python book", 2500, quantity=2)
    assert cart.totals() == {"subtotal": 5000, "discount": 0, "shipping": 0, "total": 5000}


def test_a_coupon_can_take_an_order_below_free_shipping():
    cart = Cart(coupon="SAVE10")
    cart.add("Python book", 2500, quantity=2)
    # 50.00 - 10% = 45.00, which is under the free shipping line.
    assert cart.totals() == {"subtotal": 5000, "discount": 500, "shipping": 499, "total": 4999}
