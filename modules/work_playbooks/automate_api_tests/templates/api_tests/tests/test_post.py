# Template from myOpenSDET: https://myopensdet.github.io/
"""POST: create something. The common checks: a valid body works, and each kind of bad
body is refused with 400 (not saved, and never a 500 crash)."""

import pytest
from conftest import BASE_URL, booking_body


def test_post_valid_booking_is_created(api, auth_headers):
    sent = booking_body()

    response = api.post(f"{BASE_URL}/booking", json=sent, timeout=15)

    assert response.status_code == 200  # this API's docs say 200; many APIs use 201
    data = response.json()
    assert data["bookingid"] > 0
    assert data["booking"] == sent
    # Clean up: delete what this test created.
    api.delete(f"{BASE_URL}/booking/{data['bookingid']}", headers=auth_headers, timeout=15)


def without(field):
    body = booking_body()
    del body[field]
    return body


@pytest.mark.parametrize(
    "body",
    [
        pytest.param(without("firstname"), id="missing firstname"),
        pytest.param(booking_body(totalprice="abc"), id="price is text"),
        pytest.param(
            booking_body(bookingdates={"checkin": "2026-12-05", "checkout": "2026-12-01"}),
            id="checkout before checkin",
        ),
    ],
)
def test_post_bad_booking_is_refused_with_400(api, auth_headers, body):
    response = api.post(f"{BASE_URL}/booking", json=body, timeout=15)
    if response.status_code == 200:  # it was saved by mistake: delete it, then fail
        booking_id = response.json()["bookingid"]
        api.delete(f"{BASE_URL}/booking/{booking_id}", headers=auth_headers, timeout=15)
    assert response.status_code == 400, f"got {response.status_code}: {response.text[:200]}"
