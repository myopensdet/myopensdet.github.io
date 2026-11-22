# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 6: classes and objects."""


class Cart:
    """A shopping cart that remembers items and works out the total."""

    def __init__(self):
        """Start with an empty list of items."""
        self.items = []

    def add(self, name: str, price: float, quantity: int = 1):
        """Add an item, as a dict with "name", "price" and "quantity"."""
        self.items.append({"name": name, "price": price, "quantity": quantity})

    def count(self) -> int:
        """How many things are in the cart, counting quantities."""
        return sum(item["quantity"] for item in self.items)

    def total(self) -> float:
        """The total price, rounded to 2 decimals."""
        return round(sum(item["price"] * item["quantity"] for item in self.items), 2)
