# Template from myOpenSDET: https://myopensdet.github.io/
from ex05_modules import days_between, is_stale, minutes_quiet

LAST_SEEN = "2026-11-22T09:12:00+00:00"


def test_days_between():
    assert days_between("2026-10-16", "2026-11-16") == 31


def test_same_day():
    assert days_between("2026-11-16", "2026-11-16") == 0


def test_across_a_leap_day():
    assert days_between("2028-02-28", "2028-03-01") == 2


def test_minutes_quiet():
    assert minutes_quiet(LAST_SEEN, "2026-11-22T09:30:00+00:00") == 18
    assert minutes_quiet(LAST_SEEN, "2026-11-22T09:12:59+00:00") == 0


def test_stale_after_the_limit():
    assert is_stale(LAST_SEEN, "2026-11-22T09:30:00+00:00") is True


def test_not_stale_at_the_limit():
    assert is_stale(LAST_SEEN, "2026-11-22T09:22:00+00:00") is False
    assert is_stale(LAST_SEEN, "2026-11-22T09:30:00+00:00", max_minutes=30) is False
