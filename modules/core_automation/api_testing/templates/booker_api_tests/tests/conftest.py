# Template from myOpenSDET: https://myopensdet.github.io/
"""Fixtures for the booking API: a client, a login token, and bookings that clean up."""

import os

import pytest
from api.auth import booker_token, secret
from api.client import ApiClient, check_status
from api.data import booking_data

BASE_URL = os.environ.get("BOOKER_URL", "https://restful-booker.herokuapp.com")

# Restful-booker answers 201 to a delete. Most APIs answer 204 No Content, or 200.
DELETED = (200, 201, 204)
# Already gone (the test deleted it itself): restful-booker answers 405, most APIs 404.
ALREADY_GONE = (404, 405)


@pytest.fixture(scope="session")
def client():
    with ApiClient(BASE_URL, timeout=15) as api:
        yield api


@pytest.fixture(scope="session")
def token(client):
    """Log in once per run. The username and password come from environment variables.

    On your own computer, a missing login skips the tests that need it, with the reason.
    In a pipeline (the CI variable is set), it fails instead: a green run with the
    login tests quietly skipped would look like they passed.
    """
    try:
        username, password = secret("BOOKER_USERNAME"), secret("BOOKER_PASSWORD")
    except LookupError as problem:
        if os.environ.get("CI"):
            pytest.fail(f"{problem}. In CI the login tests must run, not be skipped.")
        pytest.skip(f"{problem} (skipped on this computer; in CI this fails)")
    return booker_token(client, username, password)


@pytest.fixture(scope="session")
def auth(token):
    """Restful-booker wants the token as a cookie."""
    return {"Cookie": f"token={token}"}


def delete_booking(client, auth, booking_id):
    """Delete a booking, and fail loudly if it is still there afterwards."""
    response = client.delete(f"/booking/{booking_id}", headers=auth)
    if response.status_code not in DELETED + ALREADY_GONE:
        raise AssertionError(
            f"Clean-up failed: DELETE /booking/{booking_id} answered {response.status_code}"
        )


@pytest.fixture
def created_bookings(client, auth):
    """A list for the ids of bookings a test creates. Each one is deleted after the
    test, even when the test failed half way."""
    ids = []
    yield ids
    for booking_id in ids:
        delete_booking(client, auth, booking_id)


@pytest.fixture
def new_booking(client, auth):
    """Create a booking for one test, and delete it afterwards, even if the test failed."""
    data = booking_data()
    response = client.post("/booking", json=data)
    check_status(response, 200)
    booking_id = response.json()["bookingid"]
    yield booking_id, data
    delete_booking(client, auth, booking_id)
