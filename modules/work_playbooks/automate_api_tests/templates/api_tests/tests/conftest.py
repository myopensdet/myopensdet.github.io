# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Shared set-up for every test file: where the API is, how to log in, and test data.

Change the three settings below for your own API. Passwords never go in this file:
set them in the terminal before you run the tests.

    macOS / Linux:  export API_USERNAME=...   export API_PASSWORD=...
    Windows:        $env:API_USERNAME="..."   $env:API_PASSWORD="..."
"""

import os

import pytest
import requests

# ---- 1. CHANGE: where your API runs (a test environment, never production) ----
BASE_URL = os.environ.get("BASE_URL", "https://restful-booker.herokuapp.com")

# ---- 2. CHANGE: how your API logs in ----
LOGIN_PATH = "/auth"


def log_in(api, username, password):
    """Return a token. Change this to match your API's login endpoint."""
    response = api.post(
        f"{BASE_URL}{LOGIN_PATH}", json={"username": username, "password": password}
    )
    assert response.status_code == 200, f"Login failed: {response.status_code} {response.text}"
    token = response.json().get("token")
    assert token, f"Login answered without a token: {response.text}"
    return token


# ---- 3. CHANGE: one valid body for creating your thing ----
def booking_body(**changes):
    """A valid booking. Pass changes to make it different: booking_body(totalprice=0)."""
    body = {
        "firstname": "Arshad",
        "lastname": "Test",
        "totalprice": 120,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-12-01", "checkout": "2026-12-03"},
        "additionalneeds": "Breakfast",
    }
    body.update(changes)
    return body


# ---- Fixtures: you rarely need to change these ----


class HiddenHeaders(dict):
    """Headers that work as normal, but show as '***' when a test fails, so a token
    never ends up in the terminal, a CI log or a report."""

    def __repr__(self):
        return "{" + ", ".join(f"{name!r}: '***'" for name in self) + "}"


@pytest.fixture(scope="session")
def api():
    """One connection for the whole run, asking for JSON answers."""
    session = requests.Session()
    session.headers["Accept"] = "application/json"
    yield session
    session.close()


@pytest.fixture(scope="session")
def auth_headers(api):
    """Log in once, and give tests the header that proves it."""
    username = os.environ.get("API_USERNAME")
    password = os.environ.get("API_PASSWORD")
    if not username or not password:
        pytest.skip("Set API_USERNAME and API_PASSWORD to run tests that need a login")
    token = log_in(api, username, password)
    # Many APIs use HiddenHeaders({"Authorization": f"Bearer {token}"}) instead.
    return HiddenHeaders({"Cookie": f"token={token}"})


@pytest.fixture
def new_booking(api, auth_headers):
    """Create a booking for one test, then delete it afterwards, even if the test fails."""
    body = booking_body()
    response = api.post(f"{BASE_URL}/booking", json=body, timeout=15)
    assert response.status_code == 200, f"Could not create test data: {response.text}"
    booking_id = response.json()["bookingid"]
    yield booking_id, body
    api.delete(f"{BASE_URL}/booking/{booking_id}", headers=auth_headers, timeout=15)
