# Template from myOpenSDET: https://myopensdet.github.io/
"""API tests. Every call is logged by helpers/api_client.py, so the report shows what happened."""

from decimal import Decimal

import pytest

from tests.conftest import TEST_USER

TEST_CARD = "4242 4242 4242 4242"  # fake; the practice shop charges nothing


@pytest.mark.smoke
def test_log_in(base_url):
    from helpers.api_client import ShopApi  # noqa: PLC0415

    assert ShopApi(base_url).log_in(**TEST_USER).status_code == 200


def test_wrong_password_is_refused(base_url):
    from helpers.api_client import ShopApi  # noqa: PLC0415

    response = ShopApi(base_url).log_in(TEST_USER["email"], "not-the-password")
    assert response.status_code == 401


def test_search_finds_books(api):
    titles = [book["title"] for book in api.books("test").json()]
    assert titles == ["Python for Testers", "Clean Tests"]


@pytest.mark.smoke
def test_express_order_adds_delivery(api):
    api.add_to_cart("Python for Testers")
    api.add_to_cart("SQL in a Week")
    response = api.place_order(
        name="Arshad Test", country="Germany", delivery="express", terms=True, card=TEST_CARD
    )
    assert response.status_code == 201
    books_and_delivery = Decimal("24.99") + Decimal("19.50") + Decimal("4.99")
    assert Decimal(response.json()["total"]) == books_and_delivery


def test_order_needs_the_terms_accepted(api):
    api.add_to_cart("Clean Tests")
    response = api.place_order(
        name="Arshad Test", country="Germany", delivery="standard", terms=False, card=TEST_CARD
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Please accept the terms of sale"
