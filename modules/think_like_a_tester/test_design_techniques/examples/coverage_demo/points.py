# Template from myOpenSDET: https://myopensdet.github.io/
"""Loyalty points. This version has a bug on purpose, for the coverage lesson.

The rules: 1 point per whole dollar. Members get double points.
A customer's first order gets 50 extra points.
"""


def points_for(order_cents: int, member: bool, first_order: bool) -> int:
    if member:
        points = order_cents // 100 * 2
    if first_order:
        points += 50
    return points
