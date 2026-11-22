# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""DELETE: remove a booking, and check it is really gone."""

from api.client import check_status
from api.data import booking_data


def test_delete_removes_the_booking(client, auth):
    booking_id = client.post("/booking", json=booking_data()).json()["bookingid"]
    response = client.delete(f"/booking/{booking_id}", headers=auth)
    # Restful-booker answers 201 here. Most APIs answer 204 No Content, or 200.
    check_status(response, 201)
    check_status(client.get(f"/booking/{booking_id}"), 404)


def test_delete_without_login_is_refused(client, new_booking):
    booking_id, _ = new_booking
    check_status(client.delete(f"/booking/{booking_id}"), 403)
    check_status(client.get(f"/booking/{booking_id}"), 200)
