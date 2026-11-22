# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""SQLite, through Python's own sqlite3. The database is one file, no server."""

import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from db_clients.base_client import as_utc
from db_clients.sql_client import SqlClient

PROJECT = Path(__file__).resolve().parents[1]


class SqliteClient(SqlClient):
    driver = "sqlite"
    placeholder = "?"

    def connect(self) -> None:
        # isolation_level=None: every statement is saved at once, like autocommit.
        self.conn = sqlite3.connect(PROJECT / self.settings["path"], isolation_level=None)
        self.conn.execute("PRAGMA foreign_keys = ON")  # SQLite ignores foreign keys without this

    def to_db(self, value):
        # sqlite3 can't store Decimal or time zones: money goes in as text, times as UTC text.
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, datetime):
            return as_utc(value).strftime("%Y-%m-%d %H:%M:%S")
        return value
