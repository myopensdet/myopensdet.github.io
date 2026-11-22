# Template from myOpenSDET: https://myopensdet.github.io/
"""GET: read something. The common checks: it's there, it's not there, the id is wrong."""

from conftest import BASE_URL


def test_get_existing_booking_returns_200_and_the_data(api, new_booking):
    booking_id, sent = new_booking

    response = api.get(f"{BASE_URL}/booking/{booking_id}", timeout=15)

    assert response.status_code == 200
    data = response.json()
    assert data["firstname"] == sent["firstname"]
    assert data["totalprice"] == sent["totalprice"]
    assert data["bookingdates"] == sent["bookingdates"]


def test_get_missing_booking_returns_404(api):
    response = api.get(f"{BASE_URL}/booking/99999999", timeout=15)
    assert response.status_code == 404


def test_get_with_text_id_returns_404_or_400(api):
    response = api.get(f"{BASE_URL}/booking/abc", timeout=15)
    assert response.status_code in (400, 404)


def test_get_list_returns_ids(api, new_booking):
    booking_id, _ = new_booking

    response = api.get(f"{BASE_URL}/booking", timeout=15)

    assert response.status_code == 200
    ids = [item["bookingid"] for item in response.json()]
    assert booking_id in ids
