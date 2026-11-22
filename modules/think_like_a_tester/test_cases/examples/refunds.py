# Template from myOpenSDET: https://myopensdet.github.io/
"""Refund rules, from the reviewed refund story (REF-1 to REF-7)."""

from datetime import date

REFUND_DAYS = 30


def refund_problem(item: dict, today: date, reason: str) -> str | None:
    """Return why a refund is refused, or None if it is allowed."""
    if item["delivered_on"] is None:
        return "Not delivered yet. Use Cancel order instead"  # REF-7
    if item["refunded"]:
        return "This item was already refunded"  # REF-2
    if (today - item["delivered_on"]).days > REFUND_DAYS:
        return "Refunds are possible up to 30 days after delivery"  # REF-1
    if item["on_sale"] and reason != "faulty":
        return "Sale items can be refunded only if faulty"  # REF-4
    return None


def refund_to(paid_with: str, card_usable: bool = True) -> str:
    """Where the money goes (REF-5 and REF-6)."""
    if paid_with == "gift card":
        return "store credit"
    if paid_with == "card" and not card_usable:
        return "store credit"
    return "same account"
