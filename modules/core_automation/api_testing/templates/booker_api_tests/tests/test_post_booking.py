# Template from myOpenSDET: https://myopensdet.github.io/
"""POST: create a booking."""

import pytest
from api.client import check_status
from api.data import booking_data
from api.schema import assert_matches_schema, load_schema


@pytest.mark.smoke
def test_create_booking(client, created_bookings):
    data = booking_data(firstname="আরশাদ")
    response = client.post("/booking", json=data)
    # Restful-booker answers 200. Most APIs answer 201 Created: check your API's docs.
    check_status(response, 200)
    body = response.json()
    # Hand the id to the clean-up first, before any check that could fail.
    created_bookings.append(body["bookingid"])
    assert_matches_schema(body, load_schema("created_booking.json"))
    assert body["booking"] == data


@pytest.mark.xfail(reason="Restful-booker answers 500 for a missing field; it should be 400")
def test_missing_field_is_a_client_error(client):
    data = booking_data()
    del data["lastname"]
    response = client.post("/booking", json=data)
    check_status(response, 400)
