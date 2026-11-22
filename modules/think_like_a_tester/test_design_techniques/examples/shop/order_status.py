# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""The life of an order: which actions are allowed in which status."""

STATUSES = ["placed", "paid", "shipped", "delivered", "cancelled", "refunded"]
ACTIONS = ["pay", "cancel", "ship", "deliver"]

# (status now, action) -> new status. Anything not listed here is not allowed.
TRANSITIONS = {
    ("placed", "pay"): "paid",
    ("placed", "cancel"): "cancelled",
    ("paid", "ship"): "shipped",
    ("paid", "cancel"): "refunded",  # cancelling after paying gives the money back
    ("shipped", "deliver"): "delivered",
}


class NotAllowedError(Exception):
    pass


class Order:
    def __init__(self) -> None:
        self.status = "placed"

    def do(self, action: str) -> str:
        new_status = TRANSITIONS.get((self.status, action))
        if new_status is None:
            raise NotAllowedError(f"Can't {action} an order that is {self.status}")
        self.status = new_status
        return new_status
