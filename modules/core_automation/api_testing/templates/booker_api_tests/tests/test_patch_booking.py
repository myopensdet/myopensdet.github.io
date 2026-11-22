# Template from myOpenSDET: https://myopensdet.github.io/
"""PATCH: change some fields, and leave the rest alone."""

from api.client import check_status


def test_patch_changes_only_what_was_sent(client, auth, new_booking):
    booking_id, data = new_booking
    response = client.patch(f"/booking/{booking_id}", json={"totalprice": 99}, headers=auth)
    check_status(response, 200)
    assert client.get(f"/booking/{booking_id}").json() == {**data, "totalprice": 99}
