# Template from myOpenSDET: https://myopensdet.github.io/
"""A shopping cart. All prices are whole cents, so 4.25 is 425."""

WELCOME5_OFF = 500
WELCOME5_MINIMUM = 2000
SAVE10_PERCENT = 10


class Cart:
    def __init__(self):
        self.items = []
        self.coupon = None

    def add(self, name: str, price: int, quantity: int = 1) -> None:
        if quantity < 1:
            raise ValueError(f"Quantity must be 1 or more, got {quantity}")
        if price < 0:
            raise ValueError(f"Price can't be negative, got {price}")
        self.items.append({"name": name, "price": price, "quantity": quantity})

    def count(self) -> int:
        return sum(item["quantity"] for item in self.items)

    def subtotal(self) -> int:
        return sum(item["price"] * item["quantity"] for item in self.items)

    def apply_coupon(self, code: str) -> None:
        code = code.strip().upper()
        if code == "WELCOME5" and self.subtotal() < WELCOME5_MINIMUM:
            raise ValueError("WELCOME5 needs an order of at least 20.00")
        if code not in {"WELCOME5", "SAVE10"}:
            raise ValueError(f"Unknown coupon: {code}")
        self.coupon = code

    def total(self) -> int:
        subtotal = self.subtotal()
        if self.coupon == "WELCOME5":
            return max(subtotal - WELCOME5_OFF, 0)
        if self.coupon == "SAVE10":
            return subtotal - subtotal * SAVE10_PERCENT // 100
        return subtotal
