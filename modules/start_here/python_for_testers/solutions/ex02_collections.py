# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Exercise 2: strings, lists and dictionaries."""


def clean_username(text: str) -> str:
    """Remove spaces at both ends, and make it lower case: "  Admin " -> "admin"."""
    return text.strip().lower()


def first_and_last(items: list) -> tuple:
    """Return the first and the last item of a list, as a pair."""
    return items[0], items[-1]


def price_of(product: dict) -> float:
    """Return the product's "price", or 0 if it has none."""
    return product.get("price", 0)
