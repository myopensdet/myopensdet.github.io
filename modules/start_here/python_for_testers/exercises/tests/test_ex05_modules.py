# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
from ex05_modules import days_between


def test_days_between():
    assert days_between("2026-10-16", "2026-11-16") == 31


def test_same_day():
    assert days_between("2026-11-16", "2026-11-16") == 0


def test_across_a_leap_day():
    assert days_between("2028-02-28", "2028-03-01") == 2
