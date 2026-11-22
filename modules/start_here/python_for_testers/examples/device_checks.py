# Template from myOpenSDET: https://myopensdet.github.io/
"""Shared device checks. Other files import them: from device_checks import is_stale"""

from datetime import datetime, timedelta


def is_valid_reading(temperature: float | None, low: float = -20.0, high: float = 60.0) -> bool:
    """True when a temperature reading is there and inside the allowed range."""
    if temperature is None:
        return False
    return low <= temperature <= high


def is_stale(
    last_seen: datetime, now: datetime, max_age: timedelta = timedelta(minutes=10)
) -> bool:
    """True when the device has not reported for longer than max_age."""
    return now - last_seen > max_age


if __name__ == "__main__":
    # Runs only with "python device_checks.py", never on import.
    print("device_checks.py was run directly")
