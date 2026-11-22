# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""A pretend nightly run with the kinds of failures a real morning has. It fails on
purpose: run it to make a report for morning_triage.py to read."""

import pytest

SLOW_PAYMENTS = {"card": 3012, "wallet": 2987, "voucher": 3105}


@pytest.mark.parametrize("method", SLOW_PAYMENTS)
def test_checkout_with(method):
    took = SLOW_PAYMENTS[method]
    assert took < 3000, f"payment provider did not answer in 3000 ms (took {took} ms)"


@pytest.mark.parametrize("page", ["home", "search", "cart", "orders"])
def test_page_loads(page):
    assert page


def test_discount_code_is_applied():
    total = {"before": 40.0, "after": 40.0}
    assert total["after"] < total["before"], "discount code SAVE10 did not change the total"


def test_order_history_is_sorted():
    dates = ["2026-11-17", "2026-11-18", "2026-11-16"]
    assert dates == sorted(dates, reverse=True), "order history is not newest first"
