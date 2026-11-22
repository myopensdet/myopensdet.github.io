# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 6: classes and objects."""


class Cart:
    """A shopping cart that remembers items and works out the total."""

    def __init__(self):
        """Start with an empty list of items."""
        raise NotImplementedError("Write your code here")

    def add(self, name: str, price: float, quantity: int = 1):
        """Add an item, as a dict with "name", "price" and "quantity"."""
        raise NotImplementedError("Write your code here")

    def count(self) -> int:
        """How many things are in the cart, counting quantities."""
        raise NotImplementedError("Write your code here")

    def total(self) -> float:
        """The total price, rounded to 2 decimals."""
        raise NotImplementedError("Write your code here")
