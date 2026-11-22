# Template from myOpenSDET: https://myopensdet.github.io/
"""Writes the app makes after it answers: check them by waiting, never by sleeping."""

from helpers.clients import check_status, wait_for


def test_order_event_is_written(api, db, cleanup, customer, book):
    response = api.post(
        "/orders", json={"customer_id": customer["id"], "book_id": book["id"], "quantity": 1}
    )
    check_status(response, 201)
    order_id = cleanup.add("orders", response.json()["id"])

    event = wait_for(
        lambda: db.one("SELECT event FROM order_events WHERE order_id = %s", (order_id,)),
        timeout=5,
        what=f"the order_created event for order {order_id}",
    )
    assert event == {"event": "order_created"}
