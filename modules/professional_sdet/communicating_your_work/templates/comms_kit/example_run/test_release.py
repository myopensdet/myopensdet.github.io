# Template from myOpenSDET: https://myopensdet.github.io/
"""A pretend release test run, to make a report for status_update.py. One test fails
on purpose; leave it out with: -k "not order_history"."""


def test_discount_code_applies():
    assert True


def test_expired_code_is_refused():
    assert True


def test_checkout_by_card():
    assert True


def test_search_by_title():
    assert True


def test_order_history_is_sorted():
    dates = ["2026-11-17", "2026-11-18", "2026-11-16"]
    assert dates == sorted(dates, reverse=True), "order history is not newest first"
