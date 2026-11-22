# Template from myOpenSDET: https://myopensdet.github.io/
"""Customers: what the API saves, and what it must refuse."""

import pytest


def test_customer_is_saved(db, customer):
    saved = db.one("SELECT email, full_name FROM customers WHERE id = %s", (customer["id"],))
    assert saved == {"email": customer["email"], "full_name": "Api Test"}


def test_same_email_twice_is_refused(api, db, customer):
    response = api.post("/customers", json={"email": customer["email"], "full_name": "Again"})

    assert response.status_code in (400, 409, 422), f"got {response.status_code}"
    same = db.value("SELECT COUNT(*) FROM customers WHERE email = %s", (customer["email"],))
    assert same == 1


@pytest.mark.xfail(
    reason="Practice API bug: email case is not ignored", raises=AssertionError, strict=True
)
def test_same_email_in_capitals_is_refused(api, db, cleanup, customer):
    response = api.post(
        "/customers", json={"email": customer["email"].upper(), "full_name": "Capitals"}
    )
    if response.status_code == 201:
        cleanup.add("customers", response.json()["id"])

    same = db.value(
        "SELECT COUNT(*) FROM customers WHERE LOWER(email) = LOWER(%s)", (customer["email"],)
    )
    assert same == 1
