# Template from myOpenSDET: https://myopensdet.github.io/
"""Pure money rules. No database, no web: the easiest code to unit test.

Money is in cents, so 5000 means $50.00.
"""

FREE_SHIPPING_FROM = 5000
SHIPPING_FEE = 499
COUPONS = {"SAVE10": 10}  # code -> percent off


def shipping_cost(subtotal_cents: int) -> int:
    if subtotal_cents == 0 or subtotal_cents >= FREE_SHIPPING_FROM:
        return 0
    return SHIPPING_FEE


def discount(subtotal_cents: int, coupon: str | None) -> int:
    if coupon is None:
        return 0
    if coupon not in COUPONS:
        raise ValueError(f"Unknown coupon: {coupon}")
    return subtotal_cents * COUPONS[coupon] // 100
