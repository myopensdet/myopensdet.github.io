# Template from myOpenSDET: https://myopensdet.github.io/
"""DELETE: remove something. The common checks: it's gone afterwards, a login is needed,
and deleting it twice is handled."""

from conftest import BASE_URL, booking_body


def create_booking(api):
    response = api.post(f"{BASE_URL}/booking", json=booking_body(), timeout=15)
    assert response.status_code == 200
    return response.json()["bookingid"]


def test_delete_removes_the_booking(api, auth_headers):
    booking_id = create_booking(api)

    response = api.delete(f"{BASE_URL}/booking/{booking_id}", headers=auth_headers, timeout=15)

    assert response.status_code in (200, 201, 204)  # this API's docs say 201
    # Read it back: is it really gone?
    assert api.get(f"{BASE_URL}/booking/{booking_id}", timeout=15).status_code == 404


def test_delete_without_login_is_refused(api, new_booking):
    booking_id, _ = new_booking

    response = api.delete(f"{BASE_URL}/booking/{booking_id}", timeout=15)

    assert response.status_code in (401, 403)
    # And it must still be there.
    assert api.get(f"{BASE_URL}/booking/{booking_id}", timeout=15).status_code == 200


def test_delete_twice_returns_404(api, auth_headers):
    booking_id = create_booking(api)
    api.delete(f"{BASE_URL}/booking/{booking_id}", headers=auth_headers, timeout=15)

    response = api.delete(f"{BASE_URL}/booking/{booking_id}", headers=auth_headers, timeout=15)

    assert response.status_code == 404, f"got {response.status_code}: {response.text[:200]}"
