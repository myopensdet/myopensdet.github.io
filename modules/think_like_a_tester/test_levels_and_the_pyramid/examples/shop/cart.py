# Template from myOpenSDET: https://myopensdet.github.io/
"""A cart puts the money rules together. Testing it checks that the parts work as one."""

from dataclasses import dataclass, field

from shop.money import discount, shipping_cost


@dataclass
class Cart:
    lines: dict[str, tuple[int, int]] = field(default_factory=dict)  # name -> (price, quantity)
    coupon: str | None = None

    def add(self, name: str, price_cents: int, quantity: int = 1) -> None:
        if not 1 <= quantity <= 10:
            raise ValueError("Quantity must be 1 to 10")
        _, already = self.lines.get(name, (price_cents, 0))
        self.lines[name] = (price_cents, already + quantity)

    def totals(self) -> dict[str, int]:
        subtotal = sum(price * quantity for price, quantity in self.lines.values())
        off = discount(subtotal, self.coupon)
        # The business rule: free shipping is decided after the discount.
        shipping = shipping_cost(subtotal - off)
        return {
            "subtotal": subtotal,
            "discount": off,
            "shipping": shipping,
            "total": subtotal - off + shipping,
        }
