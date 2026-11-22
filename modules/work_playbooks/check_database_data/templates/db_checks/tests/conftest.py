# Template from myOpenSDET: https://myopensdet.github.io/
"""The database connection for every test. Set the address in the terminal, never in a file:

    macOS / Linux:  export DATABASE_URL=postgresql://user:password@host:port/database
    Windows:        $env:DATABASE_URL="postgresql://user:password@host:port/database"

The connection is READ-ONLY: these tests can look at data, never change it. Ask your team
for a read-only database user too, so even a mistake can't change anything.
"""

import os

import psycopg
import pytest

DATABASE_URL = os.environ.get("DATABASE_URL")


@pytest.fixture(scope="session")
def db():
    if not DATABASE_URL:
        pytest.skip("Set DATABASE_URL to the database you want to check")
    with psycopg.connect(DATABASE_URL) as conn:
        conn.read_only = True  # any INSERT, UPDATE or DELETE fails
        yield conn
        conn.rollback()


def rows(db, sql, params=None):
    """Run a query and return all rows as a list of tuples."""
    return db.execute(sql, params).fetchall()


def problems(found, what):
    """A clear failure message: how many, what, and the first 10 rows."""
    return f"{len(found)} {what}: {found[:10]}"
