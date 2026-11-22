# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""The same order, read from four databases: raw Python types, then normalized."""

import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1] / "templates" / "multi_db_tests"
sys.path.insert(0, str(PROJECT))

from db_clients import load_config, make_client, read_env_file  # noqa: E402
from db_clients.base_client import normalize  # noqa: E402

read_env_file(PROJECT / ".env")
config = load_config(PROJECT / "config" / "databases.yaml")

for name, settings in config["databases"].items():
    client = make_client(name, settings)
    client.connect()
    order = next(row for row in client.fetch("orders") if row["id"] == 2)
    client.close()
    total, created_at = order["total"], order["created_at"]
    print(f"{name:9} raw:  total={total!r}  created_at={created_at!r}")
    print(f"{'':9} same: total={normalize(total)!r}  created_at={normalize(created_at)!r}")
