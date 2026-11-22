# Template from myOpenSDET: https://myopensdet.github.io/
"""Test data for bookings."""


def booking_data(**changes) -> dict:
    """A valid booking. Change any field: booking_data(totalprice=0)."""
    data = {
        "firstname": "Test",
        "lastname": "Booker",
        "totalprice": 120,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-12-01", "checkout": "2026-12-03"},
        "additionalneeds": "Breakfast",
    }
    return {**data, **changes}
