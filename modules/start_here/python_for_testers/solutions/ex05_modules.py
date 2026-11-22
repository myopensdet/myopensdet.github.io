# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 5: modules and imports. Replace each raise line with your code."""

from datetime import date, datetime, timedelta


def days_between(start: str, end: str) -> int:
    """Days from start to end, both written like "2026-10-16"."""
    return (date.fromisoformat(end) - date.fromisoformat(start)).days


def minutes_quiet(last_seen: str, now: str) -> int:
    """Whole minutes between two ISO times, like "2026-11-22T09:12:00+00:00"."""
    gap = datetime.fromisoformat(now) - datetime.fromisoformat(last_seen)
    return int(gap.total_seconds() // 60)


def is_stale(last_seen: str, now: str, max_minutes: int = 10) -> bool:
    """True when the device has been quiet for longer than max_minutes."""
    gap = datetime.fromisoformat(now) - datetime.fromisoformat(last_seen)
    return gap > timedelta(minutes=max_minutes)
