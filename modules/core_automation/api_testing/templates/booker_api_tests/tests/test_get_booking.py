# Template from myOpenSDET: https://myopensdet.github.io/
"""GET: read a booking."""

import pytest
from api.client import check_status
from api.schema import assert_matches_schema, load_schema


@pytest.mark.smoke
def test_get_returns_the_saved_booking(client, new_booking):
    booking_id, data = new_booking
    response = client.get(f"/booking/{booking_id}")
    check_status(response, 200)
    assert response.json() == data
    assert_matches_schema(response.json(), load_schema("booking.json"))


def test_get_unknown_booking_is_404(client):
    response = client.get("/booking/999999999")
    check_status(response, 404)


def test_response_is_json(client, new_booking):
    booking_id, _ = new_booking
    response = client.get(f"/booking/{booking_id}")
    assert response.headers["Content-Type"].startswith("application/json")
