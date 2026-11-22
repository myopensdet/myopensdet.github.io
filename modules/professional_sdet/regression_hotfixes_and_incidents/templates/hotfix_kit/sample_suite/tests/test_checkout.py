# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
import pytest

pytestmark = [pytest.mark.checkout, pytest.mark.regression]


@pytest.mark.smoke
def test_pay_by_card():
    assert True


def test_pay_with_voucher():
    assert True


def test_refund_full_order():
    assert True


def test_refund_one_item():
    assert True
