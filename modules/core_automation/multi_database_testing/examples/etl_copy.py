# Template from myOpenSDET: https://myopensdet.github.io/
"""A copy job from PostgreSQL to MySQL, with three bugs a real one might have.

It's the thing under test in the migration lesson. Don't copy it into real work.
"""

import sys
from datetime import timedelta
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1] / "templates" / "multi_db_tests"
sys.path.insert(0, str(PROJECT))

from db_clients import load_config, make_client, read_env_file  # noqa: E402

read_env_file(PROJECT / ".env")
config = load_config(PROJECT / "config" / "databases.yaml")["databases"]

source = make_client("postgres", config["postgres"])
target = make_client("mysql", config["mysql"])
source.connect()
target.connect()

customers = source.fetch("customers")
for row in customers:
    row["full_name"] = row["full_name"][:30]  # bug 1: "names are never that long"

orders = [row for row in source.fetch("orders") if row["status"] != "cancelled"]  # bug 2
for row in orders:
    # bug 3: writes Dhaka time (UTC+6) into a column the readers treat as UTC
    row["created_at"] = row["created_at"].replace(tzinfo=None) + timedelta(hours=6)

target.create_tables()
target.insert("customers", customers)
target.insert("orders", orders)
print(f"Copied {len(customers)} customers and {len(orders)} orders to MySQL")
source.close()
target.close()
