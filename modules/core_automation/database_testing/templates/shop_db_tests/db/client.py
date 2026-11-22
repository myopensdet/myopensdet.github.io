# Template from myOpenSDET: https://myopensdet.github.io/
"""A small database client for tests: one place for the connection, queries and logging."""

import logging
import os
from contextlib import AbstractContextManager
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

log = logging.getLogger("db")


def database_url() -> str:
    """The connection address, from the environment. Never written in a file."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise LookupError("Set the environment variable DATABASE_URL first")
    return url


def connect(url: str | None = None) -> psycopg.Connection:
    """Open a connection. Rows come back as dicts: row["email"], not row[1]."""
    return psycopg.connect(
        url or database_url(), autocommit=True, row_factory=dict_row, connect_timeout=5
    )


class DbClient:
    """Run queries on one connection. Every test uses the same helpers, set once here."""

    def __init__(self, conn: psycopg.Connection):
        self.conn = conn

    def _run(self, sql: str, params) -> psycopg.Cursor:
        # Log the query and how many values were sent, never the values: they can be personal data.
        log.info("SQL %s | %d values", " ".join(sql.split()), len(params or ()))
        return self.conn.execute(sql, params)

    def all(self, sql: str, params=None) -> list[dict]:
        """Every row, as a list of dicts."""
        return self._run(sql, params).fetchall()

    def one(self, sql: str, params=None) -> dict | None:
        """The first row, or None when there are no rows."""
        return self._run(sql, params).fetchone()

    def value(self, sql: str, params=None):
        """The first column of the first row. Handy for COUNT(*) and RETURNING id."""
        row = self.one(sql, params)
        if row is None:
            raise AssertionError(f"Expected a row, got none from: {' '.join(sql.split())}")
        return next(iter(row.values()))

    def run(self, sql: str, params=None) -> int:
        """INSERT, UPDATE or DELETE. Returns how many rows changed."""
        return self._run(sql, params).rowcount

    def run_file(self, path: str | Path) -> None:
        """Run a whole .sql file, for example the schema or the seed data."""
        log.info("SQL file %s", Path(path).name)
        self.conn.execute(Path(path).read_text(encoding="utf-8"))

    def columns(self, table: str) -> dict[str, dict]:
        """What the database says a table looks like: column name -> type and nullable."""
        rows = self.all(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = current_schema() AND table_name = %s
            ORDER BY ordinal_position
            """,
            (table,),
        )
        return {
            r["column_name"]: {"type": r["data_type"], "nullable": r["is_nullable"] == "YES"}
            for r in rows
        }

    def savepoint(self) -> AbstractContextManager:
        """A block that is undone on its own if it fails. Wrap a query you expect to fail."""
        return self.conn.transaction()
