# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""A tiny shop cart. Practice code with planted bugs: don't copy it into real work."""

import logging

from shop.discounts import percent_off

log = logging.getLogger(__name__)


class Cart:
    def __init__(self, items=[]):  # noqa: B006  (planted bug: one list shared by every cart)
        self.items = items

    def add(self, name: str, price: float, quantity: int = 1) -> None:
        self.items.append((name, price, quantity))

    def total(self, discount_code: str | None = None) -> float:
        subtotal = sum(price * quantity for _, price, quantity in self.items)
        off = percent_off(discount_code)
        log.debug("subtotal=%s off=%s%%", subtotal, off)
        return subtotal * (100 - off) / 100
