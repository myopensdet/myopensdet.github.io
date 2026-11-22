# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""The two things an API + database test talks to: the API, and the database behind it."""

import logging
import os
import time

import psycopg
import requests
from psycopg.rows import dict_row

log = logging.getLogger("api_db")


def setting(name: str) -> str:
    """A setting from the environment. Never written in a file."""
    value = os.environ.get(name)
    if not value:
        raise LookupError(f"Set the environment variable {name} first")
    return value


class Api:
    """requests with a base URL, a timeout and a log line for every call."""

    def __init__(self, base_url: str, timeout: float = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        response = self.session.request(method, f"{self.base_url}{path}", **kwargs)
        log.info("%s %s -> %s", method, path, response.status_code)
        return response

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)


def check_status(response: requests.Response, expected: int) -> None:
    if response.status_code != expected:
        raise AssertionError(
            f"{response.request.method} {response.request.path_url} returned "
            f"{response.status_code}, expected {expected}: {response.text[:300]!r}"
        )


class Db:
    """Read and seed the app's database. Autocommit: the app must see what we write."""

    def __init__(self, url: str):
        self.conn = psycopg.connect(url, row_factory=dict_row, autocommit=True, connect_timeout=5)

    def one(self, sql: str, params=None) -> dict | None:
        return self.conn.execute(sql, params).fetchone()

    def all(self, sql: str, params=None) -> list[dict]:
        return self.conn.execute(sql, params).fetchall()

    def value(self, sql: str, params=None):
        row = self.one(sql, params)
        if row is None:
            raise AssertionError(f"Expected a row, got none from: {' '.join(sql.split())}")
        return next(iter(row.values()))

    def run(self, sql: str, params=None) -> int:
        return self.conn.execute(sql, params).rowcount

    def close(self) -> None:
        self.conn.close()


def wait_for(check, timeout: float = 5, every: float = 0.2, what: str = "the condition"):
    """Ask again and again until check() gives a value, or fail after timeout seconds.

    For writes the app makes after it answers: background jobs, queues, events.
    """
    deadline = time.monotonic() + timeout
    while True:
        result = check()
        if result:
            return result
        if time.monotonic() >= deadline:
            raise AssertionError(f"Waited {timeout} s for {what}, it never happened")
        time.sleep(every)


class Cleanup:
    """Remembers every row a test made, and deletes them afterwards, newest first.

    Rollback can't undo these rows: the app saved them through its own connection.
    """

    def __init__(self, db: Db):
        self.db = db
        self.rows: list[tuple[str, int]] = []

    def add(self, table: str, row_id: int) -> int:
        self.rows.append((table, row_id))
        return row_id

    def run(self) -> None:
        problems = []
        for table, row_id in reversed(self.rows):  # orders before the customer they point at
            try:
                # Table names come from the tests themselves, never from user input.
                self.db.run(f"DELETE FROM {table} WHERE id = %s", (row_id,))  # noqa: S608
            except psycopg.Error as error:
                problems.append(f"{table} {row_id}: {error}")
        if problems:
            raise AssertionError("Clean-up failed, rows left behind:\n" + "\n".join(problems))
