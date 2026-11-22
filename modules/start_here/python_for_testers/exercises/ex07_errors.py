# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 7: exception handling. Replace each raise NotImplementedError line."""


def parse_battery(text: str) -> int:
    """Turn "87" into 87.

    Raise ValueError("Battery must be a whole number from 0 to 100, got '...'")
    for text that is not a whole number, or a number outside 0 to 100.
    """
    raise NotImplementedError("Write your code here")


def safe_int(text: str, default: int = 0) -> int:
    """Turn text into an int, or return default if it isn't a whole number."""
    raise NotImplementedError("Write your code here")
