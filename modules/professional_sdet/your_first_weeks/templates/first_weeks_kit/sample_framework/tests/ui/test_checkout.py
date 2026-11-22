# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
import pytest

PAYMENT_PAGE = "https://pay.partner.example.net/checkout"


@pytest.mark.slow
def test_checkout_with_card(page, base_url):
    page.goto(base_url + "/cart")
    page.get_by_role("button", name="Checkout").click()
    page.wait_for_timeout(4000)
    assert page.url.startswith(PAYMENT_PAGE)
