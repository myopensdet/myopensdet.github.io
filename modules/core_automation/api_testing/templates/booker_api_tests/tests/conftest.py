# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Fixtures for the booking API: a client, a login token, and bookings that clean up."""

import os

import pytest
from api.auth import booker_token, secret
from api.client import ApiClient, check_status
from api.data import booking_data

BASE_URL = os.environ.get("BOOKER_URL", "https://restful-booker.herokuapp.com")


@pytest.fixture(scope="session")
def client():
    with ApiClient(BASE_URL, timeout=15) as api:
        yield api


@pytest.fixture(scope="session")
def token(client):
    """Log in once per run. The username and password come from environment variables."""
    try:
        username, password = secret("BOOKER_USERNAME"), secret("BOOKER_PASSWORD")
    except LookupError as problem:
        pytest.skip(str(problem))
    return booker_token(client, username, password)


@pytest.fixture(scope="session")
def auth(token):
    """Restful-booker wants the token as a cookie."""
    return {"Cookie": f"token={token}"}


@pytest.fixture
def new_booking(client, auth):
    """Create a booking for one test, and delete it afterwards, even if the test failed."""
    data = booking_data()
    response = client.post("/booking", json=data)
    check_status(response, 200)
    booking_id = response.json()["bookingid"]
    yield booking_id, data
    client.delete(f"/booking/{booking_id}", headers=auth)
