# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 7: errors and exceptions."""


def parse_age(text: str) -> int:
    """Turn "30" into 30. Raise ValueError with a clear message for anything else."""
    try:
        return int(text)
    except ValueError:
        raise ValueError(f"Age must be a whole number, got '{text}'") from None


def safe_int(text: str, default: int = 0) -> int:
    """Turn text into an int, or return default if it isn't a whole number."""
    try:
        return int(text)
    except ValueError:
        return default
