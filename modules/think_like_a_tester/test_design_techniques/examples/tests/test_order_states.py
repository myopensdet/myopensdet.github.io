# Template from myOpenSDET: https://myopensdet.github.io/
"""State transitions: every allowed move works, and every other move is refused."""

import pytest
from shop.order_status import NotAllowedError, Order

# Written from the rules in the story, not copied from the code.
# If the tests used the code's own table, a wrong table would pass its own tests.
STATUSES = ["placed", "paid", "shipped", "delivered", "cancelled", "refunded"]
ACTIONS = ["pay", "cancel", "ship", "deliver"]

# The paths to reach each status from a new order.
PATH_TO = {
    "placed": [],
    "paid": ["pay"],
    "shipped": ["pay", "ship"],
    "delivered": ["pay", "ship", "deliver"],
    "cancelled": ["cancel"],
    "refunded": ["pay", "cancel"],
}

ALLOWED = [
    ("placed", "pay", "paid"),
    ("placed", "cancel", "cancelled"),
    ("paid", "ship", "shipped"),
    ("paid", "cancel", "refunded"),
    ("shipped", "deliver", "delivered"),
]

# Every other pair of status and action must be refused.
NOT_ALLOWED = [
    (status, action)
    for status in STATUSES
    for action in ACTIONS
    if (status, action) not in [(start, act) for start, act, _ in ALLOWED]
]


def order_in(status):
    order = Order()
    for action in PATH_TO[status]:
        order.do(action)
    assert order.status == status
    return order


@pytest.mark.parametrize(("start", "action", "end"), ALLOWED)
def test_allowed_moves(start, action, end):
    order = order_in(start)
    assert order.do(action) == end


@pytest.mark.parametrize(("start", "action"), NOT_ALLOWED)
def test_every_other_move_is_refused(start, action):
    order = order_in(start)
    with pytest.raises(NotAllowedError, match=f"Can't {action} an order that is {start}"):
        order.do(action)
    assert order.status == start  # a refused move changes nothing


def test_the_happy_path_from_start_to_end():
    order = Order()
    for action in ["pay", "ship", "deliver"]:
        order.do(action)
    assert order.status == "delivered"
