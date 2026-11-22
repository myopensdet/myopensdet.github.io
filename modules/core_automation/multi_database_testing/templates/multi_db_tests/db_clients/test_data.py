# Template from myOpenSDET: https://myopensdet.github.io/
"""Read the test data from test_data/*.csv, with the right Python type for every column."""

import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

TEST_DATA = Path(__file__).resolve().parents[1] / "test_data"

# CSV files only hold text. These say what each column really is.
TYPES = {
    "customers": {"id": int},
    "orders": {
        "id": int,
        "customer_id": int,
        "total": Decimal,
        "created_at": datetime.fromisoformat,
    },
}

# Load order matters: orders point at customers.
TABLES = ["customers", "orders"]


def read_rows(table: str) -> list[dict]:
    with (TEST_DATA / f"{table}.csv").open(encoding="utf-8", newline="") as f:
        lines = (line for line in f if not line.startswith("#"))
        rows = list(csv.DictReader(lines))
    types = TYPES.get(table, {})
    return [{col: types.get(col, str)(value) for col, value in row.items()} for row in rows]


def load_all(client) -> None:
    """Fresh tables with the test data, in one database."""
    client.create_tables()
    for table in TABLES:
        client.insert(table, read_rows(table))
