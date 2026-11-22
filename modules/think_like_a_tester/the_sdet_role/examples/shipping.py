# Template from myOpenSDET: https://myopensdet.github.io/
"""A small piece of a real shop: what an order pays for shipping.

The rule from the user story: "Orders of $50.00 or more ship free.
Smaller orders pay $4.99." Money is in cents, so 5000 means $50.00.
"""

FREE_SHIPPING_FROM = 5000
SHIPPING_FEE = 499


def shipping_cost(subtotal_cents: int) -> int:
    if subtotal_cents == 0:
        return 0  # an empty cart has nothing to ship
    if subtotal_cents >= FREE_SHIPPING_FROM:
        return 0
    return SHIPPING_FEE
