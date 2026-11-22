# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Data integrity: the same checks, run on every database.

The checks read normalized rows, so one test works on SQL and MongoDB alike.
"""

from collections import Counter

from db_clients.test_data import read_rows

STATUSES = {"new", "paid", "shipped", "cancelled"}


def test_row_counts_match_the_test_data(db):
    for table in ("customers", "orders"):
        assert db.count(table) == len(read_rows(table)), f"{db.name}.{table}"


def test_emails_are_unique_ignoring_case(db):
    emails = Counter(row["email"].lower() for row in db.rows("customers", "id"))
    assert [email for email, n in emails.items() if n > 1] == []


def test_every_order_has_a_real_customer(db):
    customer_ids = {row["id"] for row in db.rows("customers", "id")}
    orphans = [
        row["id"] for row in db.rows("orders", "id") if row["customer_id"] not in customer_ids
    ]
    assert orphans == []


def test_order_values_are_valid(db):
    for row in db.rows("orders", "id"):
        assert row["status"] in STATUSES, row
        assert float(row["total"]) > 0, row


def test_names_keep_every_letter(db):
    """Accents and long names are where copies between databases break first."""
    names = {row["id"]: row["full_name"] for row in db.rows("customers", "id")}
    assert names["3"] == "Zoë Exämple"
    assert names["5"] == "María José Fernández-Castillo Example"


def test_orders_per_month(db):
    """The same question, asked in each database's own query language."""
    result = [(row["month"], int(row["orders"])) for row in db.run_query("orders_per_month")]
    assert result == [("2026-10", 3), ("2026-11", 5)]
