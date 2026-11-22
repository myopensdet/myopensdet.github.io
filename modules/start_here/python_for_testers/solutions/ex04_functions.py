# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 4: functions. Replace each raise line with your code."""


def make_user(name: str, role: str = "customer") -> dict:
    """Fake test user: {"name": name, "role": role, "email": "<name>@example.com"}."""
    return {"name": name, "role": role, "email": f"{name}@example.com"}


def percent(part: int, whole: int) -> float:
    """part as a percentage of whole, rounded to 1 decimal. 0.0 when whole is 0."""
    if whole == 0:
        return 0.0
    return round(part / whole * 100, 1)


def battery_ok(device: dict, minimum: int = 20) -> bool:
    """True when the device has a "battery" value of at least minimum."""
    battery = device.get("battery")
    if battery is None:
        return False
    return battery >= minimum
