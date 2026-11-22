# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 4: functions."""


def make_user(name: str, role: str = "customer") -> dict:
    """Build a test user: {"name": name, "role": role, "email": "<name>@example.com"}."""
    return {"name": name, "role": role, "email": f"{name}@example.com"}


def percent(part: int, whole: int) -> float:
    """part as a percentage of whole, rounded to 1 decimal. 0.0 when whole is 0."""
    if whole == 0:
        return 0.0
    return round(part / whole * 100, 1)
