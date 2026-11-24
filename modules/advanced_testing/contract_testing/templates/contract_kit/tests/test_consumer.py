# Template from myOpenSDET: https://myopensdet.github.io/
"""Consumer side (the orders team). Each test says what orders sends to stock, and
what it needs back. Pact answers from a mock server, and the `pact` fixture
(conftest.py) writes each passing test into pacts/orders-stock.json."""

import pytest
from pact import match
from stock_client import NotFound, StockClient


def test_get_an_item(pact):
    (
        pact.upon_receiving("a request for an item")
        .given("SNS-0042 is in stock")
        .with_request("GET", "/stock/SNS-0042")
        .will_respond_with(200)
        .with_body(
            {
                "sku": "SNS-0042",
                "available": match.int(40),  # any whole number
                "price_cents": match.int(2499),
            },
            content_type="application/json",
        )
    )
    with pact.serve() as mock:
        item = StockClient(str(mock.url)).get_item("SNS-0042")
    assert item.price_cents == 2499


def test_an_unknown_item(pact):
    (
        pact.upon_receiving("a request for an item that does not exist")
        .given("there is no item ZZ-9999")
        .with_request("GET", "/stock/ZZ-9999")
        .will_respond_with(404)
    )
    with pact.serve() as mock, pytest.raises(NotFound):
        StockClient(str(mock.url)).get_item("ZZ-9999")


def test_reserve_items(pact):
    (
        pact.upon_receiving("a reservation")
        .given("SNS-0042 is in stock")
        .with_request("POST", "/reservations")
        .with_body({"sku": "SNS-0042", "qty": 2}, content_type="application/json")
        .will_respond_with(201)
        .with_body({"reservation_id": match.str("r1")}, content_type="application/json")
    )
    with pact.serve() as mock:
        assert StockClient(str(mock.url)).reserve("SNS-0042", 2) == "r1"
