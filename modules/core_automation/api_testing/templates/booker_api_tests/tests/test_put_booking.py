# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""PUT: replace a whole booking."""

from api.client import check_status
from api.data import booking_data


def test_put_replaces_the_booking(client, auth, new_booking):
    booking_id, _ = new_booking
    changed = booking_data(totalprice=150, additionalneeds="Late checkout")
    response = client.put(f"/booking/{booking_id}", json=changed, headers=auth)
    check_status(response, 200)
    assert client.get(f"/booking/{booking_id}").json() == changed


def test_put_without_login_is_refused(client, new_booking):
    booking_id, data = new_booking
    response = client.put(f"/booking/{booking_id}", json=booking_data(totalprice=0))
    check_status(response, 403)
    assert client.get(f"/booking/{booking_id}").json() == data
