# Template from myOpenSDET: https://myopensdet.github.io/
"""Automated test cases for the refund story, each linked to the criteria it checks."""

from datetime import date

import pytest
from refunds import refund_problem, refund_to

TODAY = date(2026, 11, 16)


def item(delivered_on=date(2026, 11, 1), refunded=False, on_sale=False):
    return {"delivered_on": delivered_on, "refunded": refunded, "on_sale": on_sale}


# Positive cases: the customer gets what the story promises.


@pytest.mark.covers("REF-1")
def test_tc01_refund_is_allowed_within_30_days():
    assert refund_problem(item(), TODAY, reason="changed my mind") is None


@pytest.mark.covers("REF-1")
def test_tc02_refund_is_allowed_on_day_30():
    assert refund_problem(item(delivered_on=date(2026, 10, 17)), TODAY, "too small") is None


@pytest.mark.covers("REF-4")
def test_tc03_a_faulty_sale_item_can_be_refunded():
    assert refund_problem(item(on_sale=True), TODAY, reason="faulty") is None


@pytest.mark.covers("REF-5")
@pytest.mark.parametrize("paid_with", ["card", "paypal"])
def test_tc04_card_and_paypal_go_back_to_the_same_account(paid_with):
    assert refund_to(paid_with) == "same account"


@pytest.mark.covers("REF-5")
def test_tc05_a_gift_card_payment_becomes_store_credit():
    assert refund_to("gift card") == "store credit"


# Negative cases: the app refuses what the story says it must refuse.


@pytest.mark.covers("REF-1")
def test_tc06_refund_is_refused_on_day_31():
    problem = refund_problem(item(delivered_on=date(2026, 10, 16)), TODAY, "too small")
    assert problem == "Refunds are possible up to 30 days after delivery"


@pytest.mark.covers("REF-2")
def test_tc07_an_item_cannot_be_refunded_twice():
    problem = refund_problem(item(refunded=True), TODAY, reason="faulty")
    assert problem == "This item was already refunded"


@pytest.mark.covers("REF-4")
def test_tc08_a_sale_item_that_is_not_faulty_is_refused():
    problem = refund_problem(item(on_sale=True), TODAY, reason="changed my mind")
    assert problem == "Sale items can be refunded only if faulty"


@pytest.mark.covers("REF-6")
def test_tc09_an_expired_card_gets_store_credit():
    assert refund_to("card", card_usable=False) == "store credit"


@pytest.mark.covers("REF-7")
def test_tc10_an_order_not_delivered_yet_is_refused():
    problem = refund_problem(item(delivered_on=None), TODAY, reason="faulty")
    assert problem == "Not delivered yet. Use Cancel order instead"
