# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Fixtures: one connection for the run, and a clean database for every test.

How the clean-up works: the whole run happens inside one transaction that is
always rolled back, and each test inside a savepoint that is always rolled back.
Nothing a test writes is ever saved, even when the test fails or the run crashes.
"""

from pathlib import Path

import pytest
from db.client import DbClient, connect, database_url

SQL = Path(__file__).resolve().parents[1] / "sql"


@pytest.fixture(scope="session")
def connection():
    try:
        url = database_url()
    except LookupError as error:
        pytest.skip(str(error))
    with connect(url) as conn, conn.transaction(force_rollback=True):
        # The demo tables go in their own schema, so they never touch real tables.
        # For your own database: delete these four lines. Your migrations make the tables.
        conn.execute("CREATE SCHEMA shop_test")
        conn.execute("SET LOCAL search_path TO shop_test")
        DbClient(conn).run_file(SQL / "schema.sql")
        DbClient(conn).run_file(SQL / "seed.sql")
        yield conn


@pytest.fixture
def db(connection):
    """A DbClient whose changes are undone after the test."""
    with connection.transaction(force_rollback=True):
        yield DbClient(connection)
