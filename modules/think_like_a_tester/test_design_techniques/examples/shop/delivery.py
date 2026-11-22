# Template from myOpenSDET: https://myopensdet.github.io/
"""Delivery fees. Money is in cents, so 5000 means $50.00.

The rules, as the product owner wrote them:
- Standard delivery is free for members, and free for orders of $50.00 or more.
  Otherwise it costs $4.99.
- Express delivery costs $9.99. Members pay $4.99. It is never free.
"""

FREE_FROM = 5000
STANDARD_FEE = 499
EXPRESS_FEE = 999
EXPRESS_MEMBER_FEE = 499


def delivery_fee(subtotal_cents: int, member: bool, express: bool) -> int:
    if express:
        return EXPRESS_MEMBER_FEE if member else EXPRESS_FEE
    if member or subtotal_cents >= FREE_FROM:
        return 0
    return STANDARD_FEE
