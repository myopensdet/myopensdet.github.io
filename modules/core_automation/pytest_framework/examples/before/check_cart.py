# Template from myOpenSDET: https://myopensdet.github.io/
"""The "before" picture: a check someone runs by hand and reads. Run: python check_cart.py"""

import sys

sys.path.insert(0, "../shop_project/src")

from shop.cart import Cart  # noqa: E402

cart = Cart()
cart.add("Pocket notebook", 425, quantity=2)
cart.add("Pen", 150)
print("total:", cart.total())
if cart.total() == 1000:
    print("OK")
else:
    print("WRONG!!")

cart.apply_coupon("WELCOME5")
print("with WELCOME5:", cart.total())
