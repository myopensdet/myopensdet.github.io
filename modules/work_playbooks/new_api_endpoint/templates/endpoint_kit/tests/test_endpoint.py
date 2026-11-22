# Template from myOpenSDET: https://myopensdet.github.io/
"""Checks for one endpoint, written from the agreed rules, not from what it does today.

Change ENDPOINT, VALID and the REFUSED table for your endpoint. Each row of REFUSED is one
rule from test_plan.md: "this input must be refused".
"""

import copy

import pytest
from conftest import BASE_URL

ENDPOINT = "/carts/add"
VALID = {"userId": 1, "products": [{"id": 144, "quantity": 4}]}


def changed(**product_fields):
    """VALID, with some fields of the first product changed."""
    body = copy.deepcopy(VALID)
    body["products"][0].update(product_fields)
    return body


def send(api, body):
    return api.post(f"{BASE_URL}{ENDPOINT}", json=body, timeout=10)


def test_a_valid_cart_is_created(api):
    response = send(api, VALID)
    assert response.status_code == 201, response.text[:300]
    cart = response.json()
    product = cart["products"][0]
    assert cart["userId"] == 1
    assert product["id"] == 144
    assert product["quantity"] == 4
    assert cart["total"] == round(product["price"] * 4, 2)


REFUSED = [
    ("missing userId", {"products": VALID["products"]}),
    ("userId is text", {**VALID, "userId": "abc"}),
    ("empty products", {**VALID, "products": []}),
    ("quantity 0", changed(quantity=0)),
    ("quantity negative", changed(quantity=-2)),
    ("quantity is text", changed(quantity="many")),
    ("unknown product", changed(id=99999)),
]


@pytest.mark.parametrize("body", [row[1] for row in REFUSED], ids=[row[0] for row in REFUSED])
def test_bad_input_is_refused(api, body):
    response = send(api, body)
    assert response.status_code == 400, f"got {response.status_code}: {response.text[:200]}"
    assert response.json().get("message"), "a refusal should say why"
