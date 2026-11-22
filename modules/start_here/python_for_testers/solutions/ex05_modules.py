# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 5: modules and imports."""

from datetime import date


def days_between(start: str, end: str) -> int:
    """Days from start to end, both written like "2026-10-16"."""
    return (date.fromisoformat(end) - date.fromisoformat(start)).days
