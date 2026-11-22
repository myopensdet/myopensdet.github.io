# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Data validation: business rules the database can't enforce on its own.

Each rule is a query that finds the rows that break it. A healthy database
returns zero rows. Add a rule every time a data bug reaches production.
"""

import pytest

RULES = {
    "order total equals the sum of its items": """
        SELECT o.id, o.total, SUM(i.quantity * i.unit_price) AS items_total
        FROM orders o JOIN order_items i ON i.order_id = o.id
        GROUP BY o.id, o.total
        HAVING o.total <> SUM(i.quantity * i.unit_price)
    """,
    "every order has at least one item": """
        SELECT o.id FROM orders o
        LEFT JOIN order_items i ON i.order_id = o.id
        WHERE i.order_id IS NULL
    """,
    "no two customers share an email, ignoring case": """
        SELECT LOWER(email) AS email, COUNT(*) AS how_many
        FROM customers GROUP BY LOWER(email) HAVING COUNT(*) > 1
    """,
    "emails look like emails": """
        SELECT id, email FROM customers WHERE email NOT LIKE '_%@_%._%'
    """,
    "updated_at is never before created_at": """
        SELECT id FROM orders WHERE updated_at < created_at
    """,
}


@pytest.mark.parametrize("rule", RULES)
def test_rule_holds(db, rule):
    broken = db.all(RULES[rule])
    assert broken == [], f"{len(broken)} rows break the rule: {broken[:5]}"


def test_rules_catch_bad_data(db):
    """Prove a rule works: break it on purpose, and it must find the row."""
    db.run("UPDATE orders SET total = total + 1 WHERE id = %s", (1,))
    assert len(db.all(RULES["order total equals the sum of its items"])) == 1
