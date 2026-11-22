# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""PUT: replace something. The common checks: it changes, the change is saved, a login is
needed, and a missing id or an incomplete body is refused."""

from conftest import BASE_URL, booking_body


def test_put_updates_the_booking(api, auth_headers, new_booking):
    booking_id, _ = new_booking
    changed = booking_body(totalprice=150)

    response = api.put(
        f"{BASE_URL}/booking/{booking_id}", json=changed, headers=auth_headers, timeout=15
    )

    assert response.status_code == 200
    assert response.json()["totalprice"] == 150
    # Read it back: was the change really saved?
    saved = api.get(f"{BASE_URL}/booking/{booking_id}", timeout=15).json()
    assert saved["totalprice"] == 150


def test_put_without_login_is_refused(api, new_booking):
    booking_id, _ = new_booking

    response = api.put(f"{BASE_URL}/booking/{booking_id}", json=booking_body(), timeout=15)

    assert response.status_code in (401, 403)


def test_put_missing_booking_returns_404(api, auth_headers):
    response = api.put(
        f"{BASE_URL}/booking/99999999", json=booking_body(), headers=auth_headers, timeout=15
    )
    assert response.status_code == 404, f"got {response.status_code}: {response.text[:200]}"


def test_put_incomplete_body_returns_400(api, auth_headers, new_booking):
    booking_id, _ = new_booking

    response = api.put(
        f"{BASE_URL}/booking/{booking_id}",
        json={"firstname": "Only"},
        headers=auth_headers,
        timeout=15,
    )

    assert response.status_code == 400
