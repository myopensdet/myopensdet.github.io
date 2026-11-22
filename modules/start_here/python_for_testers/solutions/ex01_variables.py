# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Exercise 1: variables and types."""


def to_cents(price: str) -> int:
    """Turn a price written as text, like "12.50", into whole cents: 1250."""
    euros, _, cents = price.partition(".")
    return int(euros) * 100 + int(cents.ljust(2, "0"))


def is_adult(age: int) -> bool:
    """True when the age is 18 or more."""
    return age >= 18
