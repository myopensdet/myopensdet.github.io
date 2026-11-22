# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Lesson: functions. Run: python functions_demo.py"""


def delivery_fee(subtotal: float, member: bool = False) -> float:
    """Free for members and for orders of 50 or more. Otherwise 4.99."""
    if member or subtotal >= 50:
        return 0.0
    return 4.99


print(delivery_fee(20))
print(delivery_fee(20, member=True))
print(delivery_fee(50))


def shout(text: str) -> None:
    print(text.upper())  # prints, but returns nothing


result = shout("done")
print(result)
