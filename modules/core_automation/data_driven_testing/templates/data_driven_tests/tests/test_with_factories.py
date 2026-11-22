# Template from myOpenSDET: https://myopensdet.github.io/
"""Tests that build their data with factories: valid by default, one change per test."""

from app.shop_rules import check_signup, order_total
from helpers.factories import make_order, make_signup


def test_a_typical_signup_is_fine():
    signup = make_signup()
    assert check_signup(signup.email, signup.password, signup.age) == []


def test_too_young_is_the_only_problem():
    signup = make_signup(age=17)
    assert check_signup(signup.email, signup.password, signup.age) == ["age"]


def test_members_never_pay_more():
    for _ in range(200):
        order = make_order()
        member = order_total(order.subtotal, order.coupon, member=True)
        guest = order_total(order.subtotal, order.coupon, member=False)
        assert member <= guest, order


def test_a_total_is_never_negative_or_more_than_the_subtotal():
    for _ in range(200):
        order = make_order()
        total = order_total(order.subtotal, order.coupon, order.member)
        assert 0 <= total <= order.subtotal, order
