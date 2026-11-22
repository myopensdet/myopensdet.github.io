# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""The code under test in this template: a shop's signup, price and shipping rules.

Replace it with your own code. It has one bug planted on purpose, for the lessons to find.
"""

import math
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def check_signup(email: str, password: str, age: int) -> list[str]:
    """The fields that break a rule, in form order. An empty list means the signup is fine."""
    problems = []
    name, at, domain = email.partition("@")
    if not name or not at or "@" in domain or "." not in domain:
        problems.append("email")
    if not 8 <= len(password) <= 64:
        problems.append("password")
    if age <= 18:  # planted bug: the rule is "18 or older", so this should be age < 18
        problems.append("age")
    return problems


def order_total(subtotal: Decimal, coupon: str | None = None, member: bool = False) -> Decimal:
    """SAVE10 takes 10% off. WELCOME5 takes 5.00 off from a 20.00 subtotal.
    Members get 5% off after the coupon. Rounded to the cent, half up."""
    if subtotal < 0:
        raise ValueError("Subtotal can't be negative")
    total = subtotal
    if coupon == "SAVE10":
        total = total * Decimal("0.90")
    elif coupon == "WELCOME5":
        if subtotal >= Decimal("20.00"):
            total = total - Decimal("5.00")
    elif coupon:
        raise ValueError(f"Unknown coupon: {coupon}")
    if member:
        total = total * Decimal("0.95")
    return max(total, Decimal("0")).quantize(CENT, rounding=ROUND_HALF_UP)


# Price for the first kilogram, and for each extra kilogram or part of one.
SHIPPING_RATES = {
    "BD": (Decimal("2.00"), Decimal("1.00")),
    "US": (Decimal("8.00"), Decimal("3.50")),
    "NO": (Decimal("12.00"), Decimal("4.00")),
}


def shipping_cost(country: str, weight_kg: Decimal) -> Decimal:
    if weight_kg <= 0:
        raise ValueError("Weight must be more than 0")
    if country not in SHIPPING_RATES:
        raise ValueError(f"We don't ship to {country}")
    first_kg, each_extra_kg = SHIPPING_RATES[country]
    extra_kgs = max(0, math.ceil(weight_kg - 1))
    return first_kg + each_extra_kg * extra_kgs
