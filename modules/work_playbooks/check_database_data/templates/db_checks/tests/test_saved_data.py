# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Was it saved correctly? After your API or UI test creates something, check the rows.

CHANGE: ORDER_NUMBER to what your test created, and the expected values to what it sent.
"""

from decimal import Decimal

from conftest import rows

ORDER_NUMBER = "BK-1001"


def test_order_is_saved_with_the_right_values(db):
    found = rows(
        db,
        "SELECT o.status, o.total, c.email FROM orders o "
        "JOIN customers c ON c.id = o.customer_id WHERE o.order_number = %s",
        (ORDER_NUMBER,),
    )
    assert found, f"{ORDER_NUMBER} is not in the database"
    assert found == [("paid", Decimal("64.48"), "arshad.test@example.com")]


def test_order_items_are_saved(db):
    found = rows(
        db,
        "SELECT p.sku, oi.quantity, oi.unit_price FROM order_items oi "
        "JOIN orders o ON o.id = oi.order_id JOIN products p ON p.id = oi.product_id "
        "WHERE o.order_number = %s ORDER BY p.sku",
        (ORDER_NUMBER,),
    )
    assert found == [
        ("BOOK-API", 2, Decimal("19.99")),
        ("BOOK-SQL", 1, Decimal("24.50")),
    ]


def test_order_total_is_the_sum_of_its_items(db):
    ((total, items_sum),) = rows(
        db,
        "SELECT o.total, sum(oi.quantity * oi.unit_price) FROM orders o "
        "JOIN order_items oi ON oi.order_id = o.id WHERE o.order_number = %s GROUP BY o.total",
        (ORDER_NUMBER,),
    )
    assert total == items_sum
