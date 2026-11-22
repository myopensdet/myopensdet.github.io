# Template from myOpenSDET: https://myopensdet.github.io/
"""What every database client can do, whatever the database underneath.

Tests talk only to DbClient. Each database gets a small class that fills in
the gaps (postgres_client.py, mysql_client.py, sqlite_client.py, mongo_client.py).
"""

import hashlib
import json
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

QUERIES = Path(__file__).resolve().parents[1] / "queries"


def as_utc(value: datetime) -> datetime:
    """A time in UTC. A time with no time zone is taken to be UTC already.

    Don't use value.astimezone(UTC) on a time with no zone: Python then assumes the
    computer's own time zone, and the result changes from one computer to the next.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def normalize(value):
    """One value, written the same way whichever database it came from.

    Each database hands back numbers, money and times as different Python types:
    Decimal('49.50'), 49.5 or Decimal128('49.50'); a time with or without a time zone.
    Comparing them raw would report differences that aren't real.
    """
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, (int, float, Decimal)):
        return format(Decimal(str(value)).normalize(), "f")  # 49.50, 49.5 -> "49.5"
    if isinstance(value, datetime):  # MySQL DATETIME and MongoDB give no time zone: UTC here
        return as_utc(value).strftime("%Y-%m-%d %H:%M:%S")
    return str(value)


class DbClient(ABC):
    """One database. Open it, set up the test tables, and read rows back."""

    driver: str  # the folder name in queries/

    def __init__(self, name: str, settings: dict):
        self.name = name
        self.settings = settings

    def __repr__(self):
        return f"<{type(self).__name__} {self.name}>"  # never the password

    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def create_tables(self) -> None:
        """Drop and re-create the test tables. Test databases only."""

    @abstractmethod
    def insert(self, table: str, rows: list[dict]) -> None: ...

    @abstractmethod
    def count(self, table: str) -> int: ...

    @abstractmethod
    def fetch(self, table: str) -> list[dict]:
        """Every row, as the database's own Python types."""

    @abstractmethod
    def columns(self, table: str) -> list[str]: ...

    @abstractmethod
    def run_query(self, name: str) -> list[dict]:
        """Run queries/<driver>/<name>: the same question, in this database's language."""

    def query_text(self, name: str, suffix: str) -> str:
        return (QUERIES / self.driver / f"{name}{suffix}").read_text(encoding="utf-8")

    def rows(self, table: str, key: str) -> list[dict]:
        """Every row, normalized and sorted by the key: ready to compare across databases."""
        found = [{col: normalize(v) for col, v in row.items()} for row in self.fetch(table)]
        return sorted(found, key=lambda row: Decimal(row[key]))

    def checksum(self, table: str, key: str) -> str:
        """A fingerprint of the whole table. Same data in any database, same fingerprint."""
        text = json.dumps(self.rows(table, key), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
